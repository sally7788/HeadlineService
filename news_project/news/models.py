from django.db import models

# Create your models here.

# models.*field docs
# https://docs.djangoproject.com/en/5.2/ref/models/fields/#django.db.models.TextField

class Publisher(models.Model):
    platform = models.CharField(max_length=90, verbose_name='발행처 이름 (예: YTN, 조선일보, KBS News)')

class News(models.Model):
    title = models.CharField(max_length=180, verbose_name='기사/영상 제목')
    publisher_id = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='news_list')
    url = models.URLField(max_length=300, verbose_name='기사/영상 원본 URL')
    published_date = models.DateTimeField(verbose_name='최초 발행일')
    view_count = models.IntegerField(verbose_name='조회수')
    crawled_at = models.DateTimeField(verbose_name='최종 크롤링 시점')

# 결과, 결과목록, 빈도수 데이터?
# 브랜치 시범 pr