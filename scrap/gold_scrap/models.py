from django.db import models

class Extracted(models.Model):
    product_name = models.TextField()
    price_usd = models.CharField(max_length=10)
    crypto_price = models.CharField(max_length=10)
    paypal_price = models.CharField(max_length=10)
    weight = models.CharField(max_length=10)
    premium = models.CharField(max_length=10)
    product_id = models.CharField(max_length=10)
    metal_content = models.CharField(max_length=20)
    purity = models.CharField(max_length=10)
    manufacture = models.CharField(max_length=20)
    product_url = models.CharField(max_length=50)
    supplier_name = models.CharField(max_length=20)
    supplier_country = models.CharField(max_length=20)
    stock = models.CharField(max_length=10)
    
    def __str__(self):
        return self.supplier_name

# Create your models here.
class Kitco(models.Model):
    product_name = models.TextField()
    price_usd = models.CharField(max_length=10)
    price_sgd = models.CharField(max_length=10)
    crypto_price = models.CharField(max_length=10)
    paypal_price = models.CharField(max_length=10)
    weight = models.CharField(max_length=10)
    premium = models.CharField(max_length=10)
    product_id = models.CharField(max_length=10)
    metal_content = models.CharField(max_length=20)
    stock = models.CharField(max_length=10)
    purity = models.CharField(max_length=10)
    manufacture = models.CharField(max_length=20)
    product_url = models.CharField(max_length=50)
    supplier_name = models.CharField(max_length=20)
    supplier_country = models.CharField(max_length=20)

    def __str__(self):
        return self.product_name
    
class SilverBullion(models.Model):
    product_name = models.TextField()
    price_usd = models.CharField(max_length=10)
    price_sgd = models.CharField(max_length=10)
    crypto_price = models.CharField(max_length=10)
    paypal_price = models.CharField(max_length=10)
    weight = models.CharField(max_length=10)
    premium = models.CharField(max_length=10)
    product_id = models.CharField(max_length=10)
    metal_content = models.CharField(max_length=20)
    stock = models.CharField(max_length=10)
    purity = models.CharField(max_length=10)
    manufacture = models.CharField(max_length=20)
    product_url = models.CharField(max_length=50)
    supplier_name = models.CharField(max_length=20)
    supplier_country = models.CharField(max_length=20)

    def __str__(self):
        return self.product_name

class IndigoPrecious(models.Model):
    product_name = models.TextField()
    price_usd = models.CharField(max_length=10)
    price_sgd = models.CharField(max_length=10)
    crypto_price = models.CharField(max_length=10)
    paypal_price = models.CharField(max_length=10)
    weight = models.CharField(max_length=10)
    premium = models.CharField(max_length=10)
    product_id = models.CharField(max_length=10)
    metal_content = models.CharField(max_length=20)
    stock = models.CharField(max_length=10)
    purity = models.CharField(max_length=10)
    manufacture = models.CharField(max_length=20)
    product_url = models.CharField(max_length=50)
    supplier_name = models.CharField(max_length=20)
    supplier_country = models.CharField(max_length=20)

    def __str__(self):
        return self.product_name

class BullionStar(models.Model):
    product_name = models.TextField()
    price_usd = models.CharField(max_length=10)
    price_sgd = models.CharField(max_length=10)
    crypto_price = models.CharField(max_length=10)
    paypal_price = models.CharField(max_length=10)
    weight = models.CharField(max_length=10)
    premium = models.CharField(max_length=10)
    product_id = models.CharField(max_length=10)
    metal_content = models.CharField(max_length=20)
    stock = models.CharField(max_length=10)
    purity = models.CharField(max_length=10)
    manufacture = models.CharField(max_length=20)
    product_url = models.CharField(max_length=50)
    supplier_name = models.CharField(max_length=20)
    supplier_country = models.CharField(max_length=20)

    def __str__(self):
        return self.product_name

class GoldCentral(models.Model):
    product_name = models.TextField()
    price_usd = models.CharField(max_length=10)
    price_sgd = models.CharField(max_length=10)
    crypto_price = models.CharField(max_length=10)
    paypal_price = models.CharField(max_length=10)
    weight = models.CharField(max_length=10)
    premium = models.CharField(max_length=10)
    product_id = models.CharField(max_length=10)
    metal_content = models.CharField(max_length=20)
    stock = models.CharField(max_length=10)
    purity = models.CharField(max_length=10)
    manufacture = models.CharField(max_length=20)
    product_url = models.CharField(max_length=50)
    supplier_name = models.CharField(max_length=20)
    supplier_country = models.CharField(max_length=20)

    def __str__(self):
        return self.product_name

class Apmex(models.Model):
    product_name = models.TextField()
    price_usd = models.CharField(max_length=10)
    price_sgd = models.CharField(max_length=10)
    crypto_price = models.CharField(max_length=10)
    paypal_price = models.CharField(max_length=10)
    weight = models.CharField(max_length=10)
    premium = models.CharField(max_length=10)
    product_id = models.CharField(max_length=10)
    metal_content = models.CharField(max_length=20)
    stock = models.CharField(max_length=10)
    purity = models.CharField(max_length=10)
    manufacture = models.CharField(max_length=20)
    product_url = models.CharField(max_length=50)
    supplier_name = models.CharField(max_length=20)
    supplier_country = models.CharField(max_length=20)

    def __str__(self):
        return self.product_name

class SDBullion(models.Model):
    product_name = models.TextField()
    price_usd = models.CharField(max_length=10)
    price_sgd = models.CharField(max_length=10)
    crypto_price = models.CharField(max_length=10)
    paypal_price = models.CharField(max_length=10)
    weight = models.CharField(max_length=10)
    premium = models.CharField(max_length=10)
    product_id = models.CharField(max_length=10)
    metal_content = models.CharField(max_length=20)
    stock = models.CharField(max_length=10)
    purity = models.CharField(max_length=10)
    manufacture = models.CharField(max_length=20)
    product_url = models.CharField(max_length=50)
    supplier_name = models.CharField(max_length=20)
    supplier_country = models.CharField(max_length=20)

    def __str__(self):
        return self.product_name