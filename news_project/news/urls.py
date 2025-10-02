from django.urls import path
from .views import *

app_name = 'newsproject'
urlpatterns = [
    path('', NewsList.as_view(), name='newslist'),
    path('<int:pk>/', NewsDetail.as_view(), name='newsdetail'),
    path('publisher/', PublisherList.as_view(), name='publisherlist'),

    path('delete_publisher/<int:pk>', DeletePublisher.as_view(), name='deletepublisher'),
    path('wordcloud/', get_wordcloud_data, name='wordclouddata'),
    path('publisher/<int:pk>/', NewsDetail.as_view(), name='publisherdetail'),

    ]
