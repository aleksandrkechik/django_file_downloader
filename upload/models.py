from django.db import models
from django.urls import reverse


def delete_expired_files():
    for e in Upload.objects.all():
        print(e)


class Upload(models.Model):

    password = models.CharField(max_length=255, blank=True, null=True)
    max_downloads = models.IntegerField()
    expire_date = models.DateTimeField()
    file_name_orig = models.CharField(max_length=255)
    file_name_local = models.CharField(max_length=255)
    user = models.CharField(max_length=255)
    # TODO: Add more fields if needed

    def get_absolute_url(self):
        return reverse("download", args=(self.id,))

    def get_delete_url(self):
        return reverse("delete", args=(self.id,))