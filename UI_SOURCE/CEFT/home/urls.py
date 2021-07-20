from django.conf.urls import url
from django.contrib import admin

from .views import HomeView, CEFTApiView

urlpatterns = [
    url(r'^$', HomeView.as_view(), name = 'home'),
    url(r'api/ceft/$', CEFTApiView.as_view(), name = 'ceft')
]
