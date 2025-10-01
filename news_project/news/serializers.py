from rest_framework import serializers
from .models import *

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['name']

    def create(self, validated_data):
        publisher = Publisher.objects.create(name=validated_data['name'])
        publisher.save()
        return publisher

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['title', 'publisher_id', 'url', 'published_date', 'view_count', 'crawled_at']
        
    def create(self, validated_data):
        news = News.objects.create(
            title=validated_data['title'],
            publisher_id=Publisher.objects.get_or_create(name=validated_data['publisher_id'])[0].id,
            url=validated_data['url'],
            published_date=validated_data['published_date'],
            view_count=validated_data['view_count'],
            crawled_at=validated_data['crawled_at']
        )
        news.save()
        return news