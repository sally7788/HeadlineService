from django.urls import path
from .views import *

app_name = 'newsproject'
urlpatterns = [
    path('news/', NewsList.as_view(), name='newslist'),
    path('news/<int:pk>/', NewsDetail.as_view(), name='newsdetail'),
    path('publisher/', PublisherList.as_view(), name='publisherlist'),
    path('publisher/<int:pk>/', NewsDetail.as_view(), name='publisherdetail'),
]
