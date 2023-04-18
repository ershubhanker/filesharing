import os
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from django.utils import timezone
from shareit.models import File

def delete_expired_files():
    """
    Deletes expired files.
    """
    files_to_delete = File.objects.filter(expires_at__lte=timezone.now())
    for file in files_to_delete:
        os.remove(file.file.path)
        file.delete()

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(delete_expired_files, 'interval', minutes=5)
    scheduler.start()
