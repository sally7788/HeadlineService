from django.contrib import admin
from .models import Publisher, News, WordCloudResult

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'publisher', 'published_date','view_count', 'crawled_at')
    search_fields = ('title', 'publisher__name')
    list_filter = ('published_date', 'publisher') #옆에 사이드바 필터 

@admin.register(WordCloudResult)
class WordCloudResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_date', 'end_date', 'created_at')
    search_fields = ('start_date',)

