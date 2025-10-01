from django.urls import path
from .views import *

app_name = 'polls'
urlpatterns = [
    path('news/', NewsList.as_view(), name='newslist'),
    path('publisher/', PublisherList.as_view(), name='publisherlist')
]
