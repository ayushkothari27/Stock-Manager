from django.conf.urls import url
from . import views
from django.views.generic import View
from stocktrainer.views import *

urlpatterns = [
    url(r'^index/', views.index_page, name='index_page'),
    url(r'^stock/(?P<stock_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^profile/(?P<user_id>[0-9]+)$', views.profile, name='profile'),
    url(r'^news/$', views.news, name='news'),
    url(r'^crypto/$',views.crypto,name='crypto'),
    url(r'^crypto/(?P<crypto_id>[0-9]+)/$',views.crypto_detail,name='crypto_detail'),
    url(r'^watchlist/(\d+)/$', views.watchlist, name='watchlist'),
    url(r'^recommend/$', views.recommend, name='recommend'),
    url(r'^initial_recombee/$', views.initial_recombee, name='initial_recombee'),
    url(r'^recombee_user/$', views.recombee_user, name='recombee_user'),
    url(r'^data_from_recombee/$', views.data_from_recombee, name='data_from_recombee'),
    url(r'^watchlist-delete/(?P<pk>[0-9]+)/$', WatchlistDeleteView.as_view(), name='watchlist_delete'),
]
