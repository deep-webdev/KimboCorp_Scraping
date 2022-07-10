from django.apps import AppConfig


class GoldScrapConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gold_scrap'
    def ready(self):
        from gold_scrap.schedular import updater
        print("Updater Started ....")
        updater.start()