from django.apps import AppConfig


class ShareitConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shareit'

    def ready(self):
        from schedule_delete import scheduler
        scheduler.start()