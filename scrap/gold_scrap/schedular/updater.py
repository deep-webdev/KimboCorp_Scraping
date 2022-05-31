from apscheduler.schedulers.background import BackgroundScheduler
from . import gold_price,goldsilvercentral


def start():
    scheduler = BackgroundScheduler(timezone="Europe/Berlin")
    print("Starting....")
    scheduler.add_job(gold_price.main_update, 'interval', minutes=1)
    scheduler.add_job(goldsilvercentral.update_data, 'interval', hours=1)
    scheduler.start()
