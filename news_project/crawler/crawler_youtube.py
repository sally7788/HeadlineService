from django.http import JsonResponse
from django.http import HttpResponse
from django.utils import timezone
import datetime
import time
import re
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

def crawl_youtube_data(request=None, crawl_until=7):
    """
    유튜브 링크로 접속해서 무한 스크롤을 하여 받아온 비디오 갯수만큼의 데이터를 크롤링
    """
    chrome_options = Options() 
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-ipc-flooding-protection")

    if os.environ.get('GITHUB_ACTIONS'):
        chrome_options.binary_location = "/usr/bin/google-chrome"
        service = Service("/usr/local/bin/chromedriver")
    else:
        chrome_bin = os.environ.get('CHROME_BIN', '/usr/bin/chromium-browser')
        if os.path.exists(chrome_bin):
            chrome_options.binary_location = chrome_bin
        service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    '''urls = [
        "https://www.youtube.com/@MBCNEWS11/videos",
        "https://www.youtube.com/@sbsnews8/videos",
        "https://www.youtube.com/@newskbs/videos",
        "https://www.youtube.com/@jtbc_news/videos",
        "https://www.youtube.com/@ytnnews24/videos",
    ]'''

    #테스트 코드
    crawl_until = 1
    urls = [
        "https://www.youtube.com/@MBCNEWS11/videos",
    ]

    try:
        for url in urls:
            driver.get(url)
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "ytd-rich-item-renderer")))
            SCROLL_PAUSE_TIME = 2
            last_height = driver.execute_script("return document.documentElement.scrollHeight")

            #정해진 비디오 갯수가 로딩될 때까지 무한 스크롤링
            while True:
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(SCROLL_PAUSE_TIME)
                
                current_videos = driver.find_elements(By.CSS_SELECTOR, "ytd-rich-item-renderer")
                elements = current_videos[-1].find_elements(By.CSS_SELECTOR, "span")
                extracted_date = 0
                for span in elements:
                    span_text = span.text.strip()
                    
                    if any(keyword in span_text for keyword in ['일 전']):
                        extracted_date = int(re.search(r'(\d+)', span_text).group(1))
                
                if extracted_date >= crawl_until:
                    print(f"로딩 성공!")
                    break
                
                new_height = driver.execute_script("return document.documentElement.scrollHeight")
                if new_height == last_height:
                    print("더 이상 로드할 영상이 없습니다.")
                    break
                
                last_height = new_height
            
            #스크롤링으로 로딩한 비디오 수가 만족할때 데이터 크롤링
            video_containers = driver.find_elements(By.CSS_SELECTOR, "ytd-rich-item-renderer")
            channel_element = driver.find_element(By.CSS_SELECTOR, "span.yt-core-attributed-string.yt-core-attributed-string--white-space-pre-wrap")
            channel_name = channel_element.text.strip()

            for container in video_containers:
                title_text = ""
                video_url = ""
                view_count = 0
                upload_date = None
                publisher = channel_name

                title_element = container.find_element(By.CSS_SELECTOR, "#video-title")
                title_text = title_element.text.strip()
                title_text = re.sub(r'\[.*?\]', '', title_text)
                title_text = re.sub(r'\(.*?\)', '', title_text)
                title_text = re.sub(r'\s*/.*$', '', title_text)
                title_text = re.sub(r'\s*ㅣ.*$', '', title_text)
                title_text = re.sub(r'\s*｜.*$', '', title_text)
                title_text = re.sub(r'\s*\|.*$', '', title_text)
                title_text = re.sub(r'\s*#.*$', '', title_text)
                title_text = re.sub(r'\d{4}년\s*\d{1,2}월\s*\d{1,2}일', '', title_text)
                title_text = re.sub(r'\d{4}\.\s*\d{1,2}\.\s*\d{1,2}', '', title_text)
                title_text = re.sub(r'\s*(다시보기|뉴스룸|뉴스데스크)\s*', ' ', title_text)
                title_text = re.sub(r'\s+', ' ', title_text).strip()
                video_url = container.find_element(By.CSS_SELECTOR, '#video-title-link').get_attribute('href')
                metadatas = container.find_elements(By.CSS_SELECTOR, "span")
                for span in metadatas:
                    span_text = span.text.strip()

                    # 조회수 추출
                    if ('조회수' in span_text or '회' in span_text) and view_count == 0:
                        view_count = trans_view_count(span_text)
                    
                    # 업로드 날짜 추출
                    elif any(keyword in span_text for keyword in ['일 전', '주 전', '개월 전', '년 전', '시간 전', '분 전']) and upload_date is None:
                        upload_date = trans_upload_date(span_text)
                now = timezone.now()
                crawled_data = {
                    "title": title_text,
                    "publisher": publisher,
                    "url": video_url,
                    "view_count": view_count,
                    "published_date": upload_date,
                    "crawled_at": now,
                }
                db_save(crawled_data)

        return JsonResponse({
                'status': 'success',
                'count': len(video_containers)
            })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'크롤링 중 오류가 발생했습니다: {str(e)}'
        })
        
    finally:
        driver.quit()
    

def trans_view_count(view) :
    """
    조회수 텍스트를 숫자로 변환
    """
    view_text = view.replace('조회수', '').replace('회', '').strip()
    view_text = view_text.replace('.', '')

    if '만' in view_text:
        number_str = int(view_text.replace('만', ''))
        number = float(number_str) 
        return int(number * 10000) 
    elif '천' in view_text:
        number_str = view_text.replace('천', '')
        number = float(number_str)
        return int(number * 1000)
    else:
        number = int(view_text)
        return number

    
def trans_upload_date(date_text):
    """
    업로드 날짜 텍스트로 업로드 시간 계산
    """
    now = timezone.now()
    time = int(re.findall(r'\d+', date_text)[0])

    if '분 전' in date_text:
        upload_time = now - datetime.timedelta(minutes=time)
    elif '시간 전' in date_text:
        upload_time = now - datetime.timedelta(hours=time)
    elif '일 전' in date_text:
        upload_time = now - datetime.timedelta(days=time)
    elif '주 전' in date_text:
        upload_time = now - datetime.timedelta(weeks=time)
    else:
        return now.date()

    return upload_time.date()


def db_save(data):
    backend_url = 'http://127.0.0.1:8000/news/headline/'

    try:
        api_data = {
            "title": data['title'],
            "publisher": data['publisher'],
            "url": data['url'],
            "published_date": data['published_date'].isoformat(),
            "view_count": data['view_count'],
            "crawled_at": data['crawled_at'].isoformat()
        }
        
        response = requests.post(
            backend_url, 
            json=api_data,
            headers={'Content-Type': 'application/json'},
        )
        
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"Unexpected error in db_save: {e}")
        return False
