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
    price = models.CharField(max_length=12, blank=True,default="")
    region = models.CharField(max_length=30, blank=True,default="")
=======
    price = models.FloatField(blank=True)
    region = models.CharField(max_length=30, blank=True)
>>>>>>> 50f39941ed393060ccd594668ad64ad6bfaf4923
    history = models.TextField(blank=True, default="NA")
    prediction = models.TextField(blank=True, default="NA")
    sentiment = models.CharField(max_length=50, blank=True, default="NA")

    # website = models.CharField(max_length=500, default="")
    # sector = models.CharField(max_length=500, default="")
    # industry = models.CharField(max_length=500, default="")
    # last_annual_total_assets = models.BigIntegerField(default=0)
    # last_annual_revenue = models.BigIntegerField(default=0)
    # last_annual_net_income = models.BigIntegerField(default=0)
    # last_annual_eps = models.FloatField(default=0)

    def __str__(self):
        return str(self.name) + ' (' + str(self.symbol) + ')'

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    name = models.CharField(max_length = 50)
    date = models.DateField(("Date"), default=datetime.date.today, blank=True)
    type_choice = (("Stock", "Stock"),("Foreign Exchange", "ForEx"),("Crypto Currency", "Crypt"))
    type = models.CharField(max_length=20, choices=type_choice, blank=True, null=True)
    quantity = models.IntegerField(default=10)
    method_type = (("Buy", "Buy"),("Sell", "Sell"))
    method = models.CharField(max_length=10, choices=method_type)
    price = models.FloatField()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    balance = models.FloatField(default=50000)
    starting_money = models.FloatField()
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
