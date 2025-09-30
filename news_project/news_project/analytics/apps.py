# analytics/apps.py
from django.apps import AppConfig

class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news_project.analytics' # 여기에 'news.analytics'가 등록되어 있어야 합니다.