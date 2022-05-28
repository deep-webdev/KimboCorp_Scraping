from django.contrib import admin
from gold_scrap.models import SilverBullion, SDBullion, Apmex, IndigoPrecious, Kitco, GoldCentral, BullionStar

# Register your models here.
admin.site.register(SilverBullion)
admin.site.register(SDBullion)
admin.site.register(Apmex)
admin.site.register(IndigoPrecious)
admin.site.register(Kitco)
admin.site.register(GoldCentral)
admin.site.register(BullionStar)

