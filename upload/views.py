import datetime

from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.utils.timezone import now
from django.views.generic import CreateView, DetailView

from send import settings
from .form import UploadForm
from .models import Upload


class UploadPage(CreateView):
    model = Upload
    form_class = UploadForm

    # TODO:
    # 1) Convert expire_duration to expire_date
    # 2) Upload and save
    # 3) Generate download and delete link
    def get_success_upload_response(self, request, upload):
        domain = request.get_host()
        download_link = domain + Upload.get_absolute_url(upload)
        delete_link = domain + Upload.get_delete_url(upload)
        return "Download link: {} <br>Delete link: {}".format(download_link, delete_link)

    def post(self, request, *args, **kwargs):
        upload_form = UploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            expire_duration = int(upload_form.data['expire_duration'])
            expire_date = now() + datetime.timedelta(0, expire_duration)
            file = request.FILES['file']
            if file.size > settings.MAX_UPLOAD_SIZE:
                return HttpResponse("File is too big")
            file_name = default_storage.save(file.name, file)
            if upload_form.data['password'] == "":
                password = None
            else:
                password = make_password(upload_form.data['password'])
            upload = Upload(
                password=password,
                max_downloads=upload_form.data['max_downloads'],
                expire_date=expire_date,
                file_name_local=file_name,
                file_name_orig=file.name,
                user=request.user)

            upload.save()
            return HttpResponse(self.get_success_upload_response(request, upload))
        else:
            return HttpResponse("Upload failed")


class Download(DetailView):
    model = Upload

    # TODO:
    # Make it so that you can't download expired files

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        entered_password = self.request.POST.get("password")
        stored_password = self.object.password
        if self.object.password is not None:
            if not check_password(entered_password, stored_password):
                return HttpResponse("invalid password")

        file_name_local = self.object.file_name_local
        if default_storage.exists(file_name_local):
            if self.object.expire_date <= now():
                return HttpResponse("File is expired")
            file_name_orig = self.object.file_name_orig
            self.object.max_downloads = self.object.max_downloads - 1
            response = HttpResponse(default_storage.open(file_name_local, mode='rb'),
                                    content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(file_name_orig)
            if self.object.max_downloads <= 0:
                default_storage.delete(self.object.file_name_local)
                self.object.delete()
            else:
                self.object.save()
            return response
        else:
            return HttpResponse("No such file")

        # TODO:
        # 1) Delete file when max_downloads is done
        # 2) Verify password securely
        # 3) Actually send the download


class Delete(DetailView):
    model = Upload
    template_name = "upload/delete.html"

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        request_user = str(self.request.user)
        uploader = self.object.user

        # TODO: Actually delete fil
        if request_user == uploader:
            default_storage.delete(self.object.file_name_local)
            self.object.delete()
            return HttpResponse("Deleted!")
        else:
            return HttpResponse("Only uploader can delete files")
