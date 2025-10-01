from django.http import HttpResponse
from . import crawler_youtube

def youtube_crawling(request):
    """YouTube 크롤링을 실행하고 간단한 응답 반환"""
    try:
        crawler_youtube.crawl_youtube_data(request)
        return HttpResponse("YouTube crawling completed successfully!")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)