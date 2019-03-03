from django.conf.urls import url
from . import views
from django.views.generic import View
from stocktrainer.views import *

urlpatterns = [
    url(r'^index/', views.index_page, name='index_page'),
    url(r'^stock/(?P<name>.*)/(?P<symbol>.*)/(?P<region>.*)$', views.detail, name='detail'),
    url(r'^login/$', views.login_user, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^login/$', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^profile/(?P<user_id>[0-9]+)$', views.profile, name='profile'),
    url(r'^news/$', views.news, name='news'),
    url(r'^crypto/$',views.crypto,name='crypto'),
    url(r'^stockform/$',views.stockform,name='stockform'),
    url(r'^crypto/(?P<crypto_id>[0-9]+)/$',views.crypto_detail,name='crypto_detail'),
    url(r'^load_time_series/$',views.load_time_series,name='load_time_series'),
    url(r'^forex/$',views.forex,name='forex'),
    url(r'^forex_detail/(?P<forex_id>[0-9]+)/$',views.forex_detail,name='forex_detail'),
    url(r'^watchlist/$', views.watchlist, name='watchlist'),
    url(r'^recommend/$', views.recommend, name='recommend'),
    url(r'^delrecom/$', views.delrecom, name='delrecom'),
    url(r'^initial_recombee/$', views.initial_recombee, name='initial_recombee'),
    url(r'^recombee_user/$', views.recombee_user, name='recombee_user'),
    url(r'^data_from_recombee/$', views.data_from_recombee, name='data_from_recombee'),
    url(r'^watchlist-delete/(?P<pk>[0-9]+)/$', WatchlistDeleteView.as_view(), name='watchlist_delete'),
    url(r'^bot/(?P<name>.*)/$', views.bot, name='bot'),
    url(r'^google_trends/(?P<name>.*)/$', views.google_trends, name='google_trends'),
    url(r'^time_series/(?P<name>.*)/(?P<symbol>.*)/(?P<region>.*)/$',views.load_time_series,name='load_time_series'),
    url(r'^sma_ema/(?P<symbol>.*)/(?P<name>.*)$',views.get_sma_ema,name='load_sma_ema'),
    #url(r'^sma_ema/$',views.get_sma_ema,name='load_sma_ema'),
    #url(r'^sentiment_analysis/(?P<symbol>.*)/$',views.load_sentiment_analysis,name='load_sentiment_analysis'),
]
