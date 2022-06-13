from apscheduler.schedulers.background import BackgroundScheduler
from . import gold_price,goldsilvercentral,indigoprecius, kitco, silverbullion, sdbullion, apmex,bullionstar


def start():
    scheduler = BackgroundScheduler(timezone="Europe/Berlin")
    scheduler.add_job(gold_price.main_update, 'interval', minutes=1)
    scheduler.add_job(goldsilvercentral.update_data, 'interval', minutes=15)
    scheduler.add_job(indigoprecius.update_data, 'interval', minutes=15)
    scheduler.add_job(kitco.update_data, 'interval', minutes=5)
    scheduler.add_job(silverbullion.update_data, 'interval', minutes=5)
    scheduler.add_job(sdbullion.update_data, 'interval', minutes=45)
    scheduler.add_job(apmex.update_data, 'interval', minutes=50)
    scheduler.add_job(goldsilvercentral.update_data, 'interval', minutes=45)
    scheduler.add_job(bullionstar.update_data, 'interval', minutes=15)
    scheduler.start()
