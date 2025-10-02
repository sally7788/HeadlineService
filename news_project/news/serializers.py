from rest_framework import serializers
from .models import *

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name']

class HeadlineSerializer(serializers.ModelSerializer):
    publisher_id = serializers.CharField()

    class Meta:
        model = Headline
        fields = ['id', 'title', 'publisher_id', 'url', 'published_date', 'view_count', 'crawled_at']
        
    def create(self, validated_data):
        publisher_name = validated_data.pop("publisher_id")
        publisher, _ = Publisher.objects.get_or_create(name=publisher_name)
        headline = Headline.objects.create(publisher_id=publisher, **validated_data)
        return headline