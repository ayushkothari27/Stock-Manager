import requests
import pandas as pd
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import *
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
import requests


API_KEY = 'FQFTFEI83XPWMSPQ'

def header_view(request):
    print("hey")
    watch_stocks = Watch.objects.all()
    #print(watch_stocks)
    #for watch in watch_stocks:
    #    print(watch)
    context = {'watch_stocks':watch_stocks}
    return render(request,'stock/header.html',context)

def save_crypto_data():
    crypto_data = pd.read_csv('D:/DataScience/digital_currency_list.csv')
    crypto_codes = crypto_data['currency code']
    crypto_names = crypto_data['currency name']
    for i in range(len(crypto_codes)):
        crypto_obj = Crypto(name=crypto_names[i],symbol=crypto_codes[i])
        crypto_obj.save()

def crypto(request):
    if(request.method=='GET' or (request.method=='POST' and 'refresh' in request.POST)):
        crypto_stocks = Crypto.objects.all()
    if request.method=='POST' and 'search' in request.POST:
        filter=request.POST.get('filter','')
        crypto_stocks=Crypto.objects.filter(name__startswith=filter)
    return render(request,'stock/crypto.html',{'crypto_stocks':crypto_stocks})

@login_required(login_url='/login/')
def index_page(request):
    #save_crypto_data()
    #header_view(request)
    if(request.method=='GET' or (request.method=='POST' and 'refresh' in request.POST)):
        all_stocks=Stock.objects.all()
    if request.method=='POST' and 'search' in request.POST:
        filter=request.POST.get('filter','')
        all_stocks=Stock.objects.filter(name__startswith=filter)
    user = request.user
    list_of_stocks = user.entries.all()

    return render(request, 'stock/index.html', {'all_stocks':all_stocks,'watch_stocks':list_of_stocks})


@login_required(login_url='/login/')
def crypto_detail(request, crypto_id):
    crypto = get_object_or_404(Crypto, id=crypto_id)
    current_data = requests.get("https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency="+crypto.symbol+"&to_currency=USD&apikey="+API_KEY)
    current_data = dict(current_data.json())
    data_dict = current_data["Realtime Currency Exchange Rate"]
    current_price = data_dict["5. Exchange Rate"]
    user = request.user
    list_of_stocks = user.entries.all()
    daily_data_30_days = requests.get("https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol="+crypto.symbol+"&market=USD&apikey="+API_KEY)
    daily_data_30_days = dict(daily_data_30_days.json())
    print(daily_data_30_days)
    print("hi")
    open_data = []
    close_data = []
    low_data = []
    high_data = []
    volume_data = []
    month = []
    
    try:
        daily_dicts = daily_data_30_days["Time Series (Digital Currency Daily)"]
        dates = list(daily_dicts.keys())

    
        print(daily_dicts[dates[0]]["1a. open (USD)"])
        for i in range(30):
            month.append(dates[i])
            open_data.append(float(daily_dicts[dates[i]]["1a. open (USD)"]))
            close_data.append(float(daily_dicts[dates[i]]["4a. close (USD)"]))
            high_data.append(float(daily_dicts[dates[i]]["2a. high (USD)"]))
            low_data.append(float(daily_dicts[dates[i]]["3a. low (USD)"]))
            volume_data.append(float(daily_dicts[dates[i]]["5. volume"]))

    except Exception as e:
        pass

    new_month = []
    '''
    for day in month:
	    day = '"'+str(day)+'"'
        
	    new_month.append(day)
    print(new_month)
    '''
    if request.method=='POST' and 'add' in request.POST:
        if request.user.is_authenticated():
            watch = Watch(user=request.user, crypto=crypto)
            watch.save()
            message="Added To WatchList"
        else:
            message="Please Login to Continue"
            return redirect('/login')
    if request.method=='POST' and 'buy' in request.POST:
        if request.user.is_authenticated:
            quantity = int(request.POST.get('quantity', ''))
            profile = Profile.objects.get(user=request.user)
            x = float(current_price)*quantity
            if(profile.balance < x):
                message="Insufficient Balance"
            else:
                bought = Buy(user=request.user, crypto=crypto,quantity=quantity, price=float(current_price))
                bought.save()
                profile.balance = profile.balance-x
                profile.save()
                message="The Stock is Bought at price "+current_price+" with current balance = "+str(profile.balance)+"\nDeducted INR= "+str(x)
        else:
            message="Please Login to Continue"
            return redirect('/login')
    if request.method=='POST' and 'sell' in request.POST:
        if request.user.is_authenticated():
            quantity = int(request.POST.get('squantity', ''))
            q = quantity
            ast = Buy.objects.filter(user=request.user, crypto=crypto)
            tq = 0
            for i in ast:
                tq = tq + i.quantity
            if(tq>=quantity):
                profile = Profile.objects.get(user=request.POST.user)
                profile.balance = profile.balance + quantity*float(current_price)
                profile.save()
                for i in ast:
                    if(quantity-i.quantity>=0):
                        quantity = quantity - i.quantity
                        i.delete()
                    else:
                        i.quantity = i.quantity - quantity
                        i.save()
                        quantity = 0
                        break
                message="Succesfully sold your "+ str(q)+" stocks. Added money "+str(quantity*float(current_price))+". Total Balance = "+str(profile.balance)+". Total Stocks Of Item Left: "+str(tq-q)
            else:
                message="Not enough Stock of this company. Owned Stocks = "+str(tq)
        else:
            message="Please Login to Continue"
            return redirect('/login')

    context = {
        'crypto':crypto,
        'current_price':current_price,
        'open_data':open_data,
        'close_data':close_data,
        'high_data':high_data,
        'low_data':low_data,
        'volume_data':volume_data,
        'month':new_month
    }

    return render(request,'stock/crypto_detail.html',context)


@login_required(login_url='/login/')
def detail(request, stock_id):
    stock=get_object_or_404(Stock, id=stock_id)
    cp=requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol='+stock.symbol+'&interval=1min&apikey='+API_KEY)
    dict_cp=dict(cp.json())
    dict_cp=dict_cp['Time Series (1min)']
    ap=[]
    vol=[]
    for i in list(dict_cp.keys())[::2]:
        ap.append(float(dict_cp[i]["4. close"]))
        vol.append(float(dict_cp[i]["5. volume"]))
    current_price=dict_cp[list(dict_cp.keys())[0]]['4. close']
    dict_of_prices={}
    data=requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol='+stock.symbol+'&apikey='+API_KEY)
    print(data)
    dict_of_prices=dict(data.json())
    date1=dict_of_prices['Time Series (Daily)'].keys()
    date=[]
    for x in date1:
        date.append(str(x))
    print(date)
    open=[]
    high=[]
    low=[]
    close=[]
    volume=[]
    user = request.user
    list_of_stocks = user.entries.all()
    for i in date:
        open.append(float(dict_of_prices['Time Series (Daily)'][i]["1. open"]))
        high.append(float(dict_of_prices['Time Series (Daily)'][i]["2. high"]))
        low.append(float(dict_of_prices['Time Series (Daily)'][i]["3. low"]))
        close.append(float(dict_of_prices['Time Series (Daily)'][i]["4. close"]))
        volume.append(float(dict_of_prices['Time Series (Daily)'][i]["5. volume"]))
    message=""
    if request.method=='POST' and 'add' in request.POST:
        if request.user.is_authenticated():
            watch = Watch(user=request.user, stock=stock)
            watch.save()
            message="Added To WatchList"
        else:
            message="Please Login to Continue"
            return redirect('/login')
    if request.method=='POST' and 'buy' in request.POST:
        if request.user.is_authenticated:
            quantity = int(request.POST.get('quantity', ''))
            profile = Profile.objects.get(user=request.user)
            x = float(current_price)*quantity
            if(profile.balance < x):
                message="Insufficient Balance"
            else:
                bought = Buy(user=request.user, stock=stock,quantity=quantity, price=float(current_price))
                bought.save()
                profile.balance = profile.balance-x
                profile.save()
                message="The Stock is Bought at price "+current_price+" with current balance = "+str(profile.balance)+"\nDeducted INR= "+str(x)
        else:
            message="Please Login to Continue"
            return redirect('/login')
    if request.method=='POST' and 'sell' in request.POST:
        if request.user.is_authenticated():
            quantity = int(request.POST.get('squantity', ''))
            q = quantity
            ast = Buy.objects.filter(user=request.user, stock=stock)
            tq = 0
            for i in ast:
                tq = tq + i.quantity
            if(tq>=quantity):
                profile = Profile.objects.get(user=request.user)
                profile.balance = profile.balance + quantity*float(current_price)
                profile.save()
                for i in ast:
                    if(quantity-i.quantity>=0):
                        quantity = quantity - i.quantity
                        i.delete()
                    else:
                        i.quantity = i.quantity - quantity
                        i.save()
                        quantity = 0
                        break
                message="Succesfully sold your "+ str(q)+" stocks. Total Balance = "+str(profile.balance)+". Total Stocks Of Item Left: "+str(tq-q)
            else:
                message="Not enough Stock of this company. Owned Stocks = "+str(tq)
        else:
            message="Please Login to Continue"
            return redirect('/login')

    context={
        'stock': stock,
        'current_price': current_price,
        'date': date,
        'open': open,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume,
        'message': message,
        'ap': ap,
        'vol': vol,
        'watch_stocks':list_of_stocks
    }
    return render(request, 'stock/detail.html', context)

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        FirstName = request.POST.get('fname', '')
        LastName = request.POST.get('lname', '')
        email = request.POST.get('email', '')
        user = User.objects.create_user(username=username, email=email, first_name=FirstName, last_name=LastName)
        user.set_password(password)
        user.save()
        profile = Profile(user=user)
        profile.save()
        login(request, user)
        return redirect('/index')
    else:
        return render(request, 'stock/registration.html', {})

def login_user(request):
    if request.user.is_authenticated:
        user = request.user
        return redirect('/profile/%s' %user.id)
    else:
        if request.method == 'POST':
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return redirect('/profile/%s' %user.id)
                else:
                    error = 'Your account is disabled.'
                    return render(request, 'stock/login.html', {'error': error})
            else:
                error = 'Incorrect Username or Password'
                return render(request, 'stock/login.html', {'error': error})
        else:
            return render(request, 'stock/login.html', {})

def logout(request):
    django_logout(request)
    return redirect('/login')

@login_required(login_url='/login/')
def profile(request, user_id):
   user = get_object_or_404(User, pk=user_id)
   list_of_stocks = user.entries.all()
   bought_stocks = user.bentries.all()
   profile = Profile.objects.get(user=user)
   current_balance = profile.balance
   return render(request, 'stock/profile.html', {'user': user, 'stocks': list_of_stocks, 'cb': current_balance, 'bs': bought_stocks})


def news(request):
    news_data = requests.get("https://newsapi.org/v2/top-headlines?sources=cnbc&apiKey=22318c0edb3f412fb605062a091e4239")
    bitcoin_data = requests.get("https://newsapi.org/v2/top-headlines?q=bitcoin&apiKey=22318c0edb3f412fb605062a091e4239")
    bit_data = dict(bitcoin_data.json())
    data = dict(news_data.json())
    articles_json = data['articles']
    bit_articles_json = bit_data['articles']
    articles_json += bit_articles_json
    
    articles = []
    
    for article in articles_json:
        articles.append(Article(title = article['title'], description = article['description'],url = article['url'],image_url=article['urlToImage']))
        
        
    context = {'articles':articles}
    #print(articles)
    #print(headlines)
    return render(request,'stock/news.html',context)


class Article():
    def __init__(self,title,description,url,image_url):
        self.title = title
        self.description = description
        self.url = url
        self.image_url = image_url

    
    def __str__(self):
        return self.url