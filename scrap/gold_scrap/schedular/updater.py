from apscheduler.schedulers.background import BackgroundScheduler
from . import gold_price


def start():
    scheduler = BackgroundScheduler()
    print("Starting....")
    scheduler.add_job(gold_price.main_update, 'cron', minute=1)