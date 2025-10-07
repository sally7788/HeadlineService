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
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # 봇 감지 우회를 위한 추가 옵션들
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User-Agent 설정 (실제 브라우저처럼 보이도록)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # GitHub Actions 환경에서 Chrome 바이너리 위치 명시적으로 설정
    if os.environ.get('GITHUB_ACTIONS'):
        chrome_options.binary_location = "/usr/bin/google-chrome"
        print("GitHub Actions 환경에서 실행 중")
        print(f"Chrome 바이너리: {chrome_options.binary_location}")
    
    # webdriver_manager를 사용한 ChromeDriver 자동 설정
    try:
        driver_path = ChromeDriverManager().install()
        print(f"ChromeDriver 경로: {driver_path}")
        service = Service(driver_path)
    except Exception as e:
        print(f"ChromeDriverManager 에러: {e}")
        if os.environ.get('GITHUB_ACTIONS'):
            import shutil
            chromedriver_path = shutil.which('chromedriver')
            if chromedriver_path:
                print(f"시스템 ChromeDriver 발견: {chromedriver_path}")
                service = Service(chromedriver_path)
            else:
                print("ChromeDriver를 찾을 수 없습니다. 기본 Service 사용")
                service = Service()
        else:
            service = Service()

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 봇 감지 우회를 위한 추가 스크립트
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("Chrome WebDriver 초기화 성공")
    except Exception as e:
        print(f"Chrome WebDriver 초기화 실패: {e}")
        raise
    
    urls = [
        "https://www.youtube.com/@MBCNEWS11/videos",
    ]
    print("크롤링 시작")

    try:
        for url in urls:
            print(f"URL 접속 시도: {url}")
            driver.get(url)
            
            # 페이지 로딩 대기
            time.sleep(5)
            
            # 실제 접속된 URL 확인
            current_url = driver.current_url
            print(f"현재 URL: {current_url}")
            
            # 페이지 제목 확인
            page_title = driver.title
            print(f"페이지 제목: {page_title}")
            
            # 페이지 소스 일부 확인 (처음 500자)
            page_source_sample = driver.page_source[:500]
            print(f"페이지 소스 샘플: {page_source_sample}")
            
            # YouTube 동의 페이지인지 확인하고 처리
            if "consent" in current_url.lower() or "before you continue" in page_source_sample.lower():
                print("YouTube 동의 페이지 감지됨. 동의 버튼 클릭 시도...")
                try:
                    # 동의 버튼 찾기 및 클릭
                    consent_buttons = [
                        "//button[contains(text(), 'Accept all')]",
                        "//button[contains(text(), 'I agree')]",
                        "//button[contains(text(), 'Accept')]",
                        "//form[@action]//button",
                    ]
                    
                    for button_xpath in consent_buttons:
                        try:
                            button = driver.find_element(By.XPATH, button_xpath)
                            button.click()
                            print(f"동의 버튼 클릭됨: {button_xpath}")
                            time.sleep(3)
                            break
                        except:
                            continue
                    
                    # 동의 후 다시 원래 URL로 이동
                    driver.get(url)
                    time.sleep(5)
                    current_url = driver.current_url
                    print(f"동의 후 현재 URL: {current_url}")
                    
                except Exception as e:
                    print(f"동의 페이지 처리 중 오류: {e}")
            
            # 목표 URL에 도달했는지 확인
            if "youtube.com" not in current_url or "videos" not in current_url:
                print("올바른 YouTube 비디오 페이지에 접속하지 못했습니다.")
                print("페이지 상태 확인을 위해 스크린샷 저장 시도...")
                
                # 디버깅을 위한 추가 정보
                try:
                    # 모든 링크 요소 찾기
                    links = driver.find_elements(By.TAG_NAME, "a")
                    print(f"페이지의 링크 개수: {len(links)}")
                    
                    # YouTube 관련 요소 찾기
                    youtube_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='youtube'], [id*='youtube']")
                    print(f"YouTube 관련 요소 개수: {len(youtube_elements)}")
                    
                except Exception as e:
                    print(f"페이지 분석 중 오류: {e}")
                
                continue
            
            # YouTube 페이지 로딩 완료 대기
            print("YouTube 페이지 로딩 대기 중...")
            try:
                # 다양한 selector로 비디오 컨테이너 대기
                wait = WebDriverWait(driver, 20)
                
                # 먼저 페이지가 완전히 로드될 때까지 대기
                wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                
                # 비디오 컨테이너 로딩 대기 (여러 selector 시도)
                video_selectors = [
                    "ytd-rich-item-renderer",
                    "ytd-video-renderer",
                    "#contents ytd-rich-item-renderer",
                    "[class*='video']"
                ]
                
                video_containers = []
                for selector in video_selectors:
                    try:
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        video_containers = driver.find_elements(By.CSS_SELECTOR, selector)
                        if video_containers:
                            print(f"비디오 컨테이너 발견: {selector} ({len(video_containers)}개)")
                            break
                    except:
                        print(f"Selector 실패: {selector}")
                        continue
                
                if not video_containers:
                    print("비디오 컨테이너를 찾을 수 없습니다.")
                    
                    # 페이지의 모든 요소 확인
                    all_elements = driver.find_elements(By.CSS_SELECTOR, "*")
                    print(f"페이지의 총 요소 개수: {len(all_elements)}")
                    
                    # div 요소들 확인
                    divs = driver.find_elements(By.TAG_NAME, "div")
                    print(f"div 요소 개수: {len(divs)}")
                    
                    continue
                
            except Exception as e:
                print(f"페이지 로딩 대기 중 오류: {e}")
                continue
            
            # 스크롤링 수행
            print("페이지 스크롤링 시작...")
            SCROLL_PAUSE_TIME = 3
            max_scrolls = 3
            scroll_count = 0
            
            while scroll_count < max_scrolls:
                print(f"스크롤 {scroll_count + 1}/{max_scrolls}")
                
                last_height = driver.execute_script("return document.documentElement.scrollHeight")
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(SCROLL_PAUSE_TIME)
                
                new_height = driver.execute_script("return document.documentElement.scrollHeight")
                
                if new_height == last_height:
                    print("더 이상 로드할 콘텐츠가 없습니다.")
                    break
                    
                scroll_count += 1
            
            # 최종 비디오 수집
            video_containers = driver.find_elements(By.CSS_SELECTOR, "ytd-rich-item-renderer")
            print(f"최종 비디오 컨테이너 수: {len(video_containers)}")
            
            if not video_containers:
                print("크롤링할 비디오가 없습니다.")
                return JsonResponse({
                    'status': 'error',
                    'message': '비디오를 찾을 수 없습니다. YouTube 페이지 구조가 변경되었거나 접근이 차단되었을 수 있습니다.'
                })
            
            # 성공적으로 비디오를 찾았다면 계속 처리...
            print("비디오 처리 시작...")
            processed_count = 0
            
            # 여기서부터는 기존 비디오 처리 로직...
            
        return JsonResponse({
            'status': 'success',
            'count': processed_count if 'processed_count' in locals() else 0,
            'message': '크롤링이 완료되었습니다.'
        })
    
    except Exception as e:
        print(f"크롤링 중 오류 발생: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'크롤링 중 오류가 발생했습니다: {str(e)}'
        })
        
    finally:
        driver.quit()
        print("Chrome WebDriver 종료")
    

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
