from django.urls import path
from .views import *

app_name = 'newsproject'
urlpatterns = [
    path('headline/', HeadlineList.as_view(), name='newslist'),
    path('headline/<int:pk>/', HeadlineDetail.as_view(), name='newsdetail'),
    path('publisher/', PublisherList.as_view(), name='publisherlist'),
    path('publisher/<int:pk>/', PublisherDetail.as_view(), name='publisherdetail'),
]
