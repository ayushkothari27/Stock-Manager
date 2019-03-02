from django.db import models
from django.contrib.auth.models import User
import datetime

class Crypto(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    current_price = models.BigIntegerField(default=0)

    def __str__(self):
        return self.name

class Stock(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, blank=True,default="")
<<<<<<< HEAD
    website = models.CharField(max_length=500, default="")
    sector = models.CharField(max_length=500, default="")
    industry = models.CharField(max_length=500, default="")


=======
    price = models.CharField(max_length=12, blank=True)
    region = models.CharField(max_length=30, blank=True)
    history = models.TextField(blank=True, default="NA")
    prediction = models.TextField(blank=True, default="NA")
    sentiment = models.CharField(max_length=50, blank=True, default="NA")

    # website = models.CharField(max_length=500, default="")
    # sector = models.CharField(max_length=500, default="")
    # industry = models.CharField(max_length=500, default="")
>>>>>>> fca8f2fd8707b6f63b9da87b119a48c2560ed269
    # last_annual_total_assets = models.BigIntegerField(default=0)
    # last_annual_revenue = models.BigIntegerField(default=0)
    # last_annual_net_income = models.BigIntegerField(default=0)
    # last_annual_eps = models.FloatField(default=0)

    def __str__(self):
        return str(self.name) + ' (' + str(self.symbol) + ')'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    balance = models.FloatField(default=50000)

    def __str__(self):
        return self.user.first_name

class Watch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entries')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='stock')
    added_on = models.DateField(("Date"), default=datetime.date.today, blank=True)


    def __str__(self):
        return self.stock.name


class Buy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bentries')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='bstock')
    quantity = models.IntegerField(default=0)
    price = models.FloatField()
    added_on = models.DateField(("Date"), default=datetime.date.today, blank=True)

    def __str__(self):
        return self.stock.name

class Forex(models.Model):
    name = models.CharField(max_length=100,default="")
    symbol = models.CharField(max_length=100,default="")
    exchange_rate = models.CharField(max_length=100,default="")


    def __str__(self):
        return self.name
