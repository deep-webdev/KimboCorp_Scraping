# Generated by Django 4.0.4 on 2022-06-02 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gold_scrap', '0002_alter_apmex_crypto_price_alter_apmex_paypal_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apmex',
            name='premium',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='bullionstar',
            name='premium',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='goldcentral',
            name='premium',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='indigoprecious',
            name='premium',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='kitco',
            name='premium',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='sdbullion',
            name='premium',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='silverbullion',
            name='premium',
            field=models.CharField(max_length=10),
        ),
    ]
