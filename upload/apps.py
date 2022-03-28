from django.apps import AppConfig


class UploadConfig(AppConfig):
    name = 'upload'

    def ready(self):
        from scheduler import scheduler
        scheduler.start()
