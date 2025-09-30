from rest_framework import serializers
from .models import *

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['platform']

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['title', 'publisher_id', 'url', 'published_date', 'view_count', 'crawled_at']
        