import sys

from apscheduler.schedulers.background import BackgroundScheduler
from django.core.files.storage import default_storage
from django.utils.timezone import now

from upload.models import Upload


def delete_expired_files():
    expired_file_entries = Upload.objects.all().filter(expire_date__lt=now())
    for entry in expired_file_entries:
        default_storage.delete(entry.file_name_local)
        entry.delete()


def start():
    scheduler = BackgroundScheduler()
    # scheduler.add_jobstore(DjangoJobStore(), "default")
    # run this job every 24 hours
    scheduler.add_job(delete_expired_files, 'interval', hours=5, name='remove_expired_files')
    scheduler.start()
    print("Scheduler started...", file=sys.stdout)
