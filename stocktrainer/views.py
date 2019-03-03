import requests
import pandas as pd
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import *
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler

from keras.models import Sequential,load_model
from keras.layers import Dense,LSTM,Dropout
import requests
from django.http import HttpResponseRedirect
from django.views.generic.edit import DeleteView

from recombee_api_client.api_client import RecombeeClient
from recombee_api_client.api_requests import AddItemProperty, SetItemValues, AddPurchase
from recombee_api_client.api_requests import RecommendItemsToItem, Batch, ResetDatabase
from recombee_api_client.api_requests import *
import random
from pprint import pprint
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()


from pytrends.request import TrendReq
pytrends = TrendReq(hl='en-US', tz=360)
# Create your views here.


ckey="7h38tcEM8IO8id2htVXO9NDoW"
csecret="A9zfCDyM8mx7P2LBaC9rkCIgoOV3P71ZCajKbn2l0tt4EnkObk"
atoken="2611228746-JSr7EbtntCKlcAjZl5PkvVFxq8sYyzhamjvYYXg"
asecret="45c3EKZBxdI86ssyoR3gypx0ffIZGFyjlgcsznft2SToD"


API_KEY = '63XAFJTFC5HF4OE9'
fenil_key = "FQFTFEI83XPWMSPQ"

client = RecombeeClient('stockmanager', 'Y9UsOCsqPBetEKgFtmatmcdBeifBwcFqgXTAYhVpu5hEPBh31DmQ18JC5w0hqqbb')

@login_required(login_url='/login/')
def stockform(request):
    if request.method == 'GET':
        return render(request, 'stock/stockform.html')
    elif request.method == 'POST':
        user = request.user
        name = request.POST.get('name', '')
        date = request.POST.get('date', '')
        type = request.POST['type_investment']
        quantity = request.POST.get('quantity', '')
        method = request.POST['type_transaction']
        price = request.POST.get('price', '')
        trans = Transaction(user=user, name=name, date=date, type=type, quantity=quantity, method=method, price=price)
        cost = float(quantity)*float(price)
        profile = Profile.objects.get(user=request.user)
        if method=="Buy":
            profile.starting_money = profile.starting_money - cost
        elif method=="Sell":
            profile.starting_money = profile.starting_money + cost
        trans.save()
        profile.save()
        return render(request, 'stock/stockform.html')

@login_required(login_url='/login/')
def stocktrain(request):
    user = request.user
    bought_stocks = user.bentries_for_train.all()
    return render(request, 'stock/stocktrain.html', context={'bs': bought_stocks})

def header_view(request):
    print("hey")
    watch_stocks = Watch.objects.all()
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
    # Recombee results
    xyz = client.send(RecommendItemsToUser(request.user.id, 5, cascade_create=True))
    print(xyz)
    all_stocks = []
    for i, value in enumerate(d['id'] for d in xyz['recomms']):
        stock = Stock.objects.get(name=value)
        all_stocks.append(stock)
    # Kushal's code
    database_stocks = Stock.objects.all()
    # Will be replaced by above


    name = []
    symbol = []
    region = []
    currency = []
    combined_list = zip(name, symbol, region, currency)
    if request.method=='POST' and 'search' in request.POST:
        search = request.POST.get('filter','')
        res = requests.get("https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=" + search + "&apikey=" + fenil_key)
        pprint(dict(res.json()))
        query_results = dict(res.json())
        for i in query_results['bestMatches']:
            name.append(i['2. name'])
            symbol.append(i['1. symbol'])
            region.append(i['4. region'])
            currency.append(i['8. currency'])
        print("hello")
        combined_list = zip(name, symbol, region, currency)
    return render(request, 'stock/index.html', {'all_stocks':all_stocks, 'combined_list': combined_list,'database':database_stocks})


def forex_detail(request,forex_id):
    #     data = dict(response.json())['Realtime Currency Exchange Rate']
    #     name = data['2. From_Currency Name']
    #     symbol = data['1. From_Currency Code']
    #     exchange_rate = data['5. Exchange Rate']
    forex = get_object_or_404(Forex,id=forex_id)
    response = requests.get('https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency='+forex.symbol+'&to_currency=NZD&apikey=22318c0edb3f412fb605062a091e4239')
    data = dict(response.json())['Realtime Currency Exchange Rate']
    ex_rate = data['5. Exchange Rate']

    daily_30_days_data = requests.get('https://www.alphavantage.co/query?function=FX_DAILY&from_symbol='+forex.symbol+'&to_symbol=USD&apikey='+API_KEY)
    daily_30_days_data = dict(daily_30_days_data.json())
    open_data = []
    close_data = []
    low_data = []
    high_data = []
    #print(daily_30_days_data)
    try:
        time_series_data = daily_30_days_data['Time Series FX (Daily)']
        dates = list(time_series_data.keys())
        #print(dates)
        #print(time_series_data[dates[0]]['1. open'])
        for i in range(30):

            open_data.append(float(time_series_data[dates[i]]['1. open']))
            close_data.append(float(time_series_data[dates[i]]['4. close']))
            high_data.append(float(time_series_data[dates[i]]['2. high']))
            low_data.append(float(time_series_data[dates[i]]['3. low']))
    except Exception as e:
        print('Error')

    last_day_low = time_series_data[dates[0]]['3. low']
    last_day_high = time_series_data[dates[0]]['2. high']
    last_day_open = time_series_data[dates[0]]['1. open']
    last_day_close = time_series_data[dates[0]]['4. close']
    print(open_data)
    context={'exchange':ex_rate,'open':open_data,'close':close_data,'high':high_data,'low':low_data,'name':forex.name,'symbol':forex.symbol,'last_day_low':last_day_low,'last_day_high':last_day_high,'last_day_open':last_day_open,'last_day_close':last_day_close}
    return render(request,'stock/forex_detail.html',context=context)



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
def detail(request, name, symbol, region):
    print('HIIIIII')
    print(name,symbol,region)
    cp=requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol='+symbol+'&interval=1min&apikey='+fenil_key)
    print(cp)
    dict_cp=dict(cp.json())
    print(dict_cp)
    dict_cp=dict_cp['Time Series (1min)']
    ap=[]
    vol=[]
    for i in list(dict_cp.keys())[::2]:
        ap.append(float(dict_cp[i]["4. close"]))
        vol.append(float(dict_cp[i]["5. volume"]))
    current_price=dict_cp[list(dict_cp.keys())[0]]['4. close']
    dict_of_prices={}
    data=requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol='+symbol+'&apikey='+fenil_key)
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
    for i in date:
        open.append(float(dict_of_prices['Time Series (Daily)'][i]["1. open"]))
        high.append(float(dict_of_prices['Time Series (Daily)'][i]["2. high"]))
        low.append(float(dict_of_prices['Time Series (Daily)'][i]["3. low"]))
        close.append(float(dict_of_prices['Time Series (Daily)'][i]["4. close"]))
        volume.append(float(dict_of_prices['Time Series (Daily)'][i]["5. volume"]))
    message=""
    print(request.method * 100)
    if request.method=='POST' and 'add' in request.POST:
        if request.user.is_authenticated():
            stock = Stock.objects.filter(symbol = symbol)
            if len(stock)==0:
                stock = Stock(name = name, symbol = symbol, region = region, price = current_price)
                stock.save()
                reqs= []
                reqs.append(SetItemValues(
                    name, #itemId
                    #values:
                    {
                      'range': current_price,
                      'region': region
                    },
                cascade_create=True))   # Use cascadeCreate for creating item with given itemId if it doesn't exist

                client.send(Batch(reqs))
            else:
                stock = stock[0]
            watch = Watch(user=request.user, stock=stock)
            watch.save()
            message="Added To WatchList"
        else:
            message="Please Login to Continue"
            return redirect('/login')
    if request.method=='POST' and 'buy' in request.POST:
        print("aaaaya"*10)
        stock = Stock.objects.filter(symbol = symbol)
        if len(stock)==0:
            stock = Stock(name = name, symbol = symbol, region = region, price = current_price)
            stock.save()
        else:
            stock = stock[0]
        if request.user.is_authenticated:
            quantity = int(request.POST.get('quantity', ''))
            if(request.POST.get('price', '')):
                buy = float(request.POST.get('price', ''))
                profile = Profile.objects.get(user=request.user)
                x = float(buy)*quantity
                if(profile.balance < x):
                    message="Insufficient Balance"
                else:
                    bought = Buy(user=request.user, stock=stock, quantity=quantity, price=float(buy))
                    bought.save()
                    profile.balance = profile.balance-x
                    profile.save()
                    transaction = Transaction(user=request.user, name=name, type="Stock", quantity=quantity,
                    method='Buy', price=float(buy))
                    transaction.save()
                    message="The Stock is Bought at price "+str(buy)+" with current balance = "+str(profile.balance)+"\nDeducted INR= "+str(x)
            else:
                profile = Profile.objects.get(user=request.user)
                x = float(current_price)*quantity
                if(profile.balance < x):
                    message="Insufficient Balance"
                else:
                    bought = Buy(user=request.user, stock=stock, quantity=quantity, price=float(current_price))
                    bought.save()
                    profile.balance = profile.balance-x
                    profile.save()
                    message="The Stock is Bought at price "+current_price+" with current balance = "+str(profile.balance)+"\nDeducted INR= "+str(x)
        else:
            message="Please Login to Continue"
            return redirect('/login')
    if request.method=='POST' and 'sell' in request.POST:
        if request.user.is_authenticated:
            quantity = int(request.POST.get('squantity', ''))
            q = quantity
            stock = Stock.objects.get(symbol=symbol)
            ast = Buy.objects.filter(user=request.user, stock=stock)
            tq = 0
            for i in ast:
                tq = tq + i.quantity
            if(tq>=quantity):
                profile = Profile.objects.get(user=request.user)
                if request.POST.get('sell_price', ''):
                    selling_price = float(request.POST.get('sell_price', ''))
                else:
                    selling_price = float(current_price)
                profile.balance = profile.balance + quantity*float(selling_price)
                profile.save()
                transaction = Transaction(user=request.user, name=name, type="Stock", quantity=quantity,
                method='Sell', price=float(selling_price))
                transaction.save()
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






    if request.method=='POST' and 'buytemp' in request.POST:
        print("aaaaya"*10)
        stock = Stock.objects.filter(symbol = symbol)
        if len(stock)==0:
            stock = Stock(name = name, symbol = symbol, region = region, price = current_price)
            stock.save()
        else:
            stock = stock[0]
        if request.user.is_authenticated:
            quantity = int(request.POST.get('bquantity', ''))
            profile = Profile.objects.get(user=request.user)
            x = float(current_price)*quantity
            if(profile.starting_money < x):
                message="Insufficient Balance"
            else:
                bought = Buyfortrain(user=request.user, stock=stock, quantity=quantity, price=float(current_price))
                bought.save()
                profile.starting_money = profile.starting_money-x
                profile.save()
                message="The Stock is virtually Bought at price "+current_price+" with current balance = "+str(profile.starting_money)+"\nDeducted INR= "+str(x)
        else:
            message="Please Login to Continue"
            return redirect('/login')
    if request.method=='POST' and 'selltemp' in request.POST:
        if request.user.is_authenticated:
            quantity = int(request.POST.get('squantity', ''))
            q = quantity
            stock = Stock.objects.filter(symbol=symbol)
            if len(stock)==0:
                message = "Buy stocks first"
            else:
                stock = stock[0]
                ast = Buyfortrain.objects.filter(user=request.user, stock=stock)
                tq = 0
                for i in ast:
                    tq = tq + i.quantity
                if(tq>=quantity):
                    profile = Profile.objects.get(user=request.user)
                    selling_price = float(current_price)
                    profile.starting_money = profile.starting_money + quantity*float(selling_price)
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
                    message="Succesfully sold your "+ str(q)+" stocks. Total Balance = "+str(profile.starting_money)+". Total Stocks Of Item Left: "+str(tq-q)
                else:
                    message="Not enough Stock of this company. Owned Stocks = "+str(tq)
        else:
            message="Please Login to Continue"
            return redirect('/login')


    context={
        'last_day_low': low[0],
        'last_day_high': high[0],
        'last_day_open': open[0],
        'last_day_close': close[0],
        'name': name,
        'symbol': symbol,
        'region': region,
        'current_price': current_price,
        'date': date,
        'open': open,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume,
        'message': message,
        'ap': ap,
        'vol': vol
    }
    return render(request, 'stock/detail.html', context)

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        FirstName = request.POST.get('fname', '')
        LastName = request.POST.get('lname', '')
        email = request.POST.get('email', '')
        print(username,FirstName,LastName,email)
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

def chatbot(request):
    return render(request, 'stock/chatbot.html')

@login_required(login_url='/login/')
def profile(request, user_id):
   user = get_object_or_404(User, pk=user_id)
   bought_stocks = user.bentries.all()
   prices = []

   for s in bought_stocks:
       print(s.stock.symbol)
    #    res = requests.get("https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=" + s.stock.sy + "&apikey=" + fenil_key)
    #    query_results = dict(res.json())
    #    symb = query_results['bestMatches'][0]['1. symbol']
       cp=requests.get('https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol='+s.stock.symbol+'&apikey='+fenil_key)
       dict_cp=dict(cp.json())
       print(dict_cp)
       price=dict_cp['Global Quote']["05. price"]
       price = (float(price) - float(s.price))*float(s.quantity)
       prices.append("{0:.2f}".format(price))


   profile = Profile.objects.get(user=user)
   history  = user.transac.all()
   send_together = zip(bought_stocks, prices)
   return render(request, 'stock/profile.html',
   {'user': user, 'history': history, 'profile': profile, 'bs': send_together})


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

def load_time_series(request,name,symbol, region):

    stocks = Stock.objects.all()
    symbols = [stock.symbol for stock in stocks]
    if symbol not in symbols:
        stocks = ['WMT','GOOG','T','MSFT','AAPL','BRK.B','FB','JPM','AMZN','BABA']
        response = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=XON&outputsize=full&apikey=FQFTFEI83XPWMSPQ")
        data = dict(response.json())
        meta_data = data['Meta Data']
        time_series = data['Time Series (Daily)']
        symbol = meta_data['2. Symbol']
        print(symbol)
        c = 0
        dates = []
        open_ = []
        for date,info in time_series.items():
            dates.append(date)
            open_.append(info['1. open'])
            c += 1
            if c>=1258:
                break

        #print(dates,open)

        open_ = list(reversed(open_))
        training_data = np.array(open_).reshape((-1,1))
        print(training_data.shape)
        #print(training_data)

        scaler = MinMaxScaler()
        training_data_scaled = scaler.fit_transform(training_data)
        print(training_data_scaled.shape)
        #print(training_data_scaled)


        X_train = []
        y_train = []
        for i in range(60,1258):
            X_train.append(training_data_scaled[i-60:i,0])
            y_train.append(training_data_scaled[i,0])
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        print(X_train.shape,y_train.shape)
        X_train = np.reshape(X_train,(X_train.shape[0],X_train.shape[1],1))


        model = Sequential()
        model.add(LSTM(units=50,return_sequences=True,input_shape=(X_train.shape[1],1)))
        model.add(Dropout(0.2))
        model.add(LSTM(units=50,return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(units=50,return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(units=50,return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(units=1))
        model.compile(optimizer='adam',metrics=['accuracy'],loss='mean_squared_error')
        model.fit(X_train,y_train,epochs=3,batch_size=32)


        file_name = str(symbol)+'.h5'
        model.save(file_name)
        #model.summary()

        inputs = open_[-80:]
        inputs = np.array(inputs,dtype=np.float32).reshape((-1,1))
        inputs = scaler.transform(inputs)


        X_test = []
        for i in range(60,80):
            X_test.append(inputs[i-60:i,0])
        X_test = np.array(X_test)
        X_test = np.reshape(X_test,(X_test.shape[0],X_test.shape[1],1))

        predictions = model.predict(X_test)
        predictions = scaler.inverse_transform(predictions)
        #print(predictions)


        historical_data = np.array(open_[-240:],dtype=np.float32)
        price = open_[-1]
        # print(type(predictions))
        # print(type(historical_data))
        pred = [i[0] for i in predictions]
        predictions = str(pred)

        historical_data = str(list(historical_data))
        print(predictions)
        print(historical_data)
        stock = Stock(name=name,symbol=symbol,prediction=predictions,history=historical_data,price=price,region=region)
        stock.save()
    else:
        stock = Stock.objects.filter(symbol=symbol)[0]
        print(stock)
    name = stock.name
    symbol = stock.symbol
    predictions = stock.prediction
    historical_data = stock.history
    price = stock.price
    print(type(predictions))
    print(historical_data)
    #pred = predictions[6:-15]
    #print(predictions)
    predictions = eval(predictions)
    print(predictions)
    print(type(predictions))
    #hist = historical_data[6:-15]
    #print(hist)
    historical_data = eval(historical_data)
    print(historical_data)
    #predictions = np.array(predictions)
    #historical_data = np.array(historical_data)
    print(type(historical_data))
    print(type(predictions))
    #historical_data = list(historical_data)
    predictions = list(np.ravel(predictions))
    print(predictions,historical_data)
    context = {'predictions':predictions,'history':historical_data}
    return render(request,'stock/time_series.html',context=context)

class Article():
    def __init__(self,title,description,url,image_url):
        self.title = title
        self.description = description
        self.url = url
        self.image_url = image_url


    def __str__(self):
        return self.url

def forex(request):

    curr_set = ['EUR','JPY','GBP','AUD','CAD','CHF','CNY','SEK','NZD','MXN','SGD','HKD','NOK','KRW','TRY','RUB','INR','BRL','ZAR']
    queryset = Forex.objects.all()
    # currencies = ['SGD']
    # for curr in currencies:
    #     response = requests.get('https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={0}&to_currency=USD&apikey=22318c0edb3f412fb605062a091e4239'.format(curr))
    #     #print(dict(response.json()))
    #     data = dict(response.json())['Realtime Currency Exchange Rate']
    #     name = data['2. From_Currency Name']
    #     symbol = data['1. From_Currency Code']
    #     exchange_rate = data['5. Exchange Rate']
    #     #print(name,symbol,exchange_rate)
    #     forex = Forex(name=name,symbol=symbol,exchange_rate=exchange_rate)
    #     forex.save()
    context = {'forex':queryset}
    return render(request,'stock/forex.html',context=context)


class WatchlistDeleteView(DeleteView):
    login_url = '/login/'
    model = Watch
    success_url = '/watchlist/'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        success_url = success_url + str(self.request.user.id)
        print(self.object)
        self.object.delete()
        return HttpResponseRedirect(success_url)

@login_required
def watchlist(request):
    user = request.user
    watch_list = Watch.objects.filter(user=user)
    print(watch_list)
    return render(request, 'stock/watchlist.html',{'watch_list':watch_list})

def recommend(request):    #database schema
    client.send(AddItemProperty('range', 'double'))
    client.send(AddItemProperty('region', 'string'))

def delrecom(request):    #database schema
    client.send(DeleteItem('Arsenal'))
    client.send(DeleteItem('BARCA'))
    client.send(DeleteItem('RMA'))
    client.send(DeleteItem('CHELASEA'))
    client.send(DeleteItem('CHELSEA'))

def initial_recombee(request): #populate recombee initially
    stock = Stock.objects.all()
    requests = []
    for i in range(3, len(stock)):
        name = stock[i].name
        price = stock[i].price
        region = stock[i].region
        requests.append(SetItemValues(
            name, #itemId
            #values:
            {
              'range': price,
              'region': region
            },
        cascade_create=True))   # Use cascadeCreate for creating item with given itemId if it doesn't exist

    client.send(Batch(requests))

def recombee_user(request):  #recombee user create
    requests = []
    requests.append(AddPurchase(2, "AA", cascade_create=True))
    requests.append(AddPurchase(2, "CHELASEA", cascade_create=True))

    client.send(Batch(requests))

def data_from_recombee(request):
    xyz = client.send(RecommendItemsToUser(2, 2))['recomms']
    print(xyz)

def bot(request,name):
    print("Hi")
    if request.method == 'POST':
            global sign
            reply = request.POST.get('reply', '')
            print(reply)
            global list_of_tweets
            global i
            global pos_count
            flag = True
            twitterStream = Stream(auth, listener())
            twitterStream.filter(track=[reply])
            print(list_of_tweets)
            block = []
            for j in range(len(list_of_tweets)):
                url = "https://api.twitter.com/1.1/statuses/oembed.json"
                params = dict(
                id = list_of_tweets[j]
                )
                resp = requests.get(url=url, params=params)
                data = resp.json()
                try:
                    aayu = data["html"].replace("<script async src=\"https://platform.twitter.com/widgets.js\" charset=\"utf-8\"></script>","")
                    block.append(aayu)
                except Exception as e:
                    pass
            if pos_count>5:
                sentiment = "The general sentiment of people is positive"
            elif pos_count>3:
                sentiment = "The general sentiment of people is nuetral"
            else:
                sentiment = "The general sentiment of people is negative"
            list_of_tweets = []
            i = 0
            pos_count = 0
            return render(request, 'stock/bot.html', {'reply':reply, 'flag':flag,'block':block, 'sentiment':sentiment})
    else:
            global sign
            reply = name
            print(reply)
            flag = True
            twitterStream = Stream(auth, listener())
            twitterStream.filter(track=[reply])
            print(list_of_tweets)
            block = []
            for j in range(len(list_of_tweets)):
                url = "https://api.twitter.com/1.1/statuses/oembed.json"
                params = dict(
                id = list_of_tweets[j]
                )
                resp = requests.get(url=url, params=params)
                data = resp.json()
                try:
                    aayu = data["html"].replace("<script async src=\"https://platform.twitter.com/widgets.js\" charset=\"utf-8\"></script>","")
                    block.append(aayu)
                except Exception as e:
                    pass
            if pos_count>5:
                sentiment = "The general sentiment of people is positive"
            elif pos_count>3:
                sentiment = "The general sentiment of people is nuetral"
            else:
                sentiment = "The general sentiment of people is negative"
            list_of_tweets = []
            i = 0
            pos_count = 0
            return render(request, 'stock/bot.html', {'reply':reply, 'flag':flag,'block':block, 'sentiment':sentiment})


i = 0
list_of_tweets = []
pos_count = 0

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

class listener(StreamListener):
    def on_data(self, data):
        global i
        global list_of_tweets
        global pos_count
        data = json.loads(data)
        try:
            if data["id"] != ' ':
                print(data["text"])
                ss = sid.polarity_scores(data["text"])
                if ss['compound']>=0:
                    list_of_tweets.append(data["id"])
                    pos_count = pos_count + 1
                    i = i + 1
                elif ss['compound']<=0:
                    list_of_tweets.append(data["id"])
                    i = i + 1
                elif sign == "":
                    list_of_tweets.append(data["id"])
                    print("signlessssssss")
                    i = i + 1
        except Exception as e:
            pass
        if i<10:
            return True
        else:
            return False

    def on_error(self, status_code):
        if status_code == 420:
            return False


def get_sma_ema(request,symbol,name):
    interval = 'daily'
    time_period = '20'
    sma_response = requests.get('https://www.alphavantage.co/query?function=SMA&symbol='+symbol+'&interval=daily&time_period=20&series_type=open&apikey=63XAFJTFC5HF4OE9')
    #print(sma_response)
    sma_data = dict(sma_response.json())['Technical Analysis: SMA']
    ema_response = requests.get('https://www.alphavantage.co/query?function=EMA&symbol='+symbol+'&interval=daily&time_period=20&series_type=open&apikey=63XAFJTFC5HF4OE9')
    #print(ema_response)
    ema_data = dict(ema_response.json())['Technical Analysis: EMA']
    sma_dates = list(sma_data.keys())
    ema_dates = list(ema_data.keys())
    #print(sma_dates)
    sma_values = []
    ema_values = []
    print(sma_data[sma_dates[0]]['SMA'])
    for i in range(60):
        sma_values.append(sma_data[sma_dates[i]]['SMA'])
        ema_values.append(ema_data[ema_dates[i]]['EMA'])

    sma_float = [float(x) for x in sma_values]
    ema_float = [float(x) for x in ema_values]

    print(sma_float,ema_float)
    context = {'sma_values':sma_float,'ema_values':ema_float,'symbol':symbol,'name':name}
    return render(request,'stock/sma_ema.html',context=context)

def google_trends(request,name):
    kw_list = [name]
    xyz = pytrends.get_historical_interest(kw_list, year_start=2019, month_start=1, day_start=1, hour_start=0, year_end=2019, month_end=2, day_end=1, hour_end=0, cat=0, geo='', gprop='', sleep=0)
    value = xyz.ix[:,0]
    value = value.tolist()
    print(value)
    date = xyz.index
    dates = []
    for time in date:
        dates.append(time.strftime("%Y-%m-%d %H:%M:%S"))
    print(dates)
    return render(request, 'stock/google_trends.html', {'value':value,'dates':dates})
