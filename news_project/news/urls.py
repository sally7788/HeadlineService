from django.urls import path
from .views import *

app_name = 'news_project'
urlpatterns = [
    path('news/', NewsList.as_view(), name='newslist'),
    path('publisher/', PublisherList.as_view(), name='publisherlist'),
    path('delete_publisher/<int:pk>', DeletePublisher.as_view(), name='deletepublisher'),
    path('wordcloud/', get_wordcloud_data, name='wordclouddata')
]
