# news/naver_crawler.py

import os
import django
import time
from datetime import datetime
from django.utils import timezone

# Django 프로젝트 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_project.settings')
django.setup()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from news.models import News, Publisher

# Selenium 드라이버 설정
def get_driver():
    options = Options()
    options.add_argument("--headless")  # 브라우저 없이 실행
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

# 네이버 인기 뉴스 크롤링
def crawl_naver_news():
    driver = get_driver()
    driver.get("https://news.naver.com/main/ranking/popularDay.naver")
    time.sleep(2)

    now = datetime.now()
    boxes = driver.find_elements(By.CSS_SELECTOR, ".rankingnews_box")

    for box in boxes:
        try:
            publisher_name = box.find_element(By.CLASS_NAME, "rankingnews_name").text.strip()
            publisher, _ = Publisher.objects.get_or_create(name=publisher_name)

            articles = box.find_elements(By.CSS_SELECTOR, "ul.rankingnews_list li")
            for article in articles:
                try:
                    link = article.find_element(By.TAG_NAME, "a")
                    title = link.text.strip()
                    href = link.get_attribute("href")

                    # 중복 뉴스는 건너뜀
                    if News.objects.filter(url=href).exists():
                        continue

                    # 상세 페이지 접속 후 발행일 추출
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[1])
                    driver.get(href)
                    time.sleep(1)

                    try:
                        date_el = driver.find_element(
                            By.CSS_SELECTOR, "span.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME"
                        )
                        published_str = date_el.get_attribute("data-date-time")
                        published_date = timezone.make_aware(
                            datetime.strptime(published_str, "%Y-%m-%d %H:%M:%S")
                        )   
                    except:
                        published_date = now

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                    # DB에 저장
                    News.objects.create(
                        publisher=publisher,
                        title=title,
                        url=href,
                        published_date=published_date,
                        crawled_at=now,
                    )

                except Exception as e:
                    print("기사 처리 오류:", e)
                    continue

        except Exception as e:
            print("박스 처리 오류:", e)
            continue

    driver.quit()
    print("크롤링 및 저장 완료.")

# 실행
if __name__ == "__main__":
    crawl_naver_news()
