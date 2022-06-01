from apscheduler.schedulers.background import BackgroundScheduler
from . import gold_price,goldsilvercentral,indigoprecius, kitco, silverbullion

def start():
    scheduler = BackgroundScheduler(timezone="Europe/Berlin")
    print("Starting....")
    scheduler.add_job(gold_price.main_update, 'interval', minutes=1)
    scheduler.add_job(goldsilvercentral.update_data, 'interval', minutes=15)
    scheduler.add_job(indigoprecius.update_data, 'interval', minutes=15)
    scheduler.add_job(kitco.update_data, 'interval', minutes=20)
    scheduler.add_job(silverbullion.update_data, 'interval', minutes=20)
    scheduler.start()
