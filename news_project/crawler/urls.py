from django.urls import path
from . import views

urlpatterns = [
    path('ycrawl/', views.youtube_crawling, name='crawl'),
]