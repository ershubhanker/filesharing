from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from schedule_delete.delfile import deletefiles

def start():
	scheduler = BackgroundScheduler()
	scheduler.add_job(deletefiles, 'interval', seconds=60)
	scheduler.start()