from django.conf.urls import url
from . import views
from django.views.generic import View
from stocktrainer.views import *

urlpatterns = [
    url(r'^index/', views.index_page, name='index_page'),
    url(r'^stock/(?P<stock_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^login/$', views.login_user, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^profile/(?P<user_id>[0-9]+)$', views.profile, name='profile'),
    url(r'^news/$', views.news, name='news'),
    url(r'^crypto/$',views.crypto,name='crypto'),
    url(r'^crypto/(?P<crypto_id>[0-9]+)/$',views.crypto_detail,name='crypto_detail'),
    url(r'^load_time_series/$',views.load_time_series,name='load_time_series'),
    url(r'^forex/$',views.forex,name='forex'),
    url(r'^forex_detail/(?P<forex_id>[0-9]+)/$',views.forex_detail,name='forex_detail'),
    url(r'^watchlist/(\d+)/$', views.watchlist, name='watchlist'),
    url(r'^watchlist-delete/(?P<pk>[0-9]+)/$', WatchlistDeleteView.as_view(), name='watchlist_delete'),
    url(r'^time_series/(?P<name>.*/(?P<symbol>.*/(?P<region>.*/$',views.load_time_series,nam)
    #url(r'^time_series/$',views.time_series_data,name='time_series_data')
]
