import os
import django

# from gold_price import main_update
import schedule
import time
from gold_scrap.schedular import gold_price,goldsilvercentral,indigoprecius, kitco, silverbullion, sdbullion, apmex,bullionstar


if __name__ == '__main__':
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scrap.settings")
    # django.setup()

    schedule.every(1).minutes.do(gold_price.main_update)
    while 1:
        schedule.run_pending()
        time.sleep(1)

