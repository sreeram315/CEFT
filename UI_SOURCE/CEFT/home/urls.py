from django.conf.urls import url
from django.contrib import admin

from .views import HomeView, CEFTApiView, CEFTTemplateView, SaliencyTemplateView, SaliencyAnalysisView

urlpatterns = [
    url(r'^$', HomeView.as_view(), name = 'home'),
    url(r'ceft/$', CEFTTemplateView.as_view(), name = 'ceft'),
    url(r'saliency/$', SaliencyTemplateView.as_view(), name = 'saliency'),
    url(r'saliency-analysis/(?P<imageId>\d+)/$', SaliencyAnalysisView.as_view(), name = 'saliency-analysis'),
    url(r'api/ceft/$', CEFTApiView.as_view(), name = 'ceft_api')
]


