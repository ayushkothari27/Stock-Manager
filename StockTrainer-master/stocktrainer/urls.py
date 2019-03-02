from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^index/', views.index_page, name='index_page'),
    url(r'^stock/(?P<stock_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^login/$', views.login_user, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^profile/(?P<user_id>[0-9]+)$', views.profile, name='profile'),
    url(r'^news/$', views.news, name='news'),
    url(r'^crypto/$',views.crypto,name='crypto'),
    url(r'^crypto/(?P<crypto_id>[0-9]+)/$',views.crypto_detail,name='crypto_detail')
]
