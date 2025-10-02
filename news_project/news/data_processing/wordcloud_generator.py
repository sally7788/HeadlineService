from datetime import date
from collections import Counter
import json
from konlpy.tag import Okt 
from django.db.models import Q, Min, Max
from datetime import datetime, timedelta

from ..models import Headline, Publisher, WordCloudResult

STOPWORDS = set([
    '뉴스', '기자', '오늘', '이슈', '속보', '있다', '것이다', '하다', '등', '이번', '그것', '지난', '합니다', '한다'
])

def generate_word_frequencies(start_date: date=None, end_date: date=None, selected_publisher_ids: list=None):
    """
    지정된 기간, 신문사 ID, 그리고 조회수(view_count)를 가중치로 사용하여
    단어 빈도수를 계산하고 WordCloudResult에 JSON 형태로 저장합니다.
    """
    okt = Okt()
    
    filters= Q()
    if selected_publisher_ids:
        filters &= Q(publisher__in=selected_publisher_ids)
        
    if start_date and end_date:# start_date와 end_date가 모두 제공된 경우에만 필터링
        try: 
            end_date_obj  = datetime.strptime(end_date, '%Y-%m-%d')
            adjusted_end_date = end_date_obj + timedelta(days=1)
            filters &= Q(published_date__gte=start_date) & Q(published_date__lt=adjusted_end_date)
        
        except ValueError:
            print(">> 날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식이어야 합니다.")
            return None
    
    # 1. 데이터 필터링 및 조회: title과 view_count를 함께 가져와야 가중치 적용이 가능합니다.
    # view_count가 없는 경우를 대비해 기본값 0을 적용합니다.
    headlines = Headline.objects.filter(filters).values('title', 'view_count', 'published_date') # 딕셔너리 형태로 조회

    if not headlines:
        print(">> 조회된 헤드라인이 없습니다. WordCloud 생성을 건너뜁니다.")
        return None
    word_counts = Counter()
    
    # 2. 텍스트 전처리, 명사 추출, 가중치 적용 (핵심 T 로직)
    for headline in headlines:
        title = headline['title']
        # 조회수(view_count)를 가중치로 사용. 값이 None이면 1로 처리하여 기본 가중치 적용.
        view_weight = headline['view_count'] if headline['view_count'] is not None and headline['view_count'] > 0 else 1
        
        nouns = okt.nouns(title) 
        
        filtered_nouns = [
            noun for noun in nouns 
            if len(noun) > 1 and noun not in STOPWORDS
        ]
        
        for noun in filtered_nouns:
            word_counts[noun] += view_weight

    # 3. 워드클라우드에 사용할 상위 100개 단어만 추출
    top_words = word_counts.most_common(100)
    
    # 4. JSON 포맷으로 변환 (프론트엔드 시각화용)
    # [{'text': '단어', 'value': 빈도수}, ...] 형태로 변환
    frequency_data = [
        {'text': word, 'value': count} 
        for word, count in top_words
    ]
    final_start_date = start_date
    final_end_date = end_date
    if not start_date or not end_date:
        
        date_range=headlines.aggregate(min_date=Min('published_date'), max_date=Max('published_date'))
        final_start_date=date_range['min_date']
        final_end_date=date_range['max_date']
    
    publishers_to_log=selected_publisher_ids
    if not selected_publisher_ids:
        publishers_to_log=Publisher.objects.all().values_list('id', flat=True)
    # 5. WordCloudResult 테이블에 결과 저장
    result_obj = WordCloudResult.objects.create(
        start_date=final_start_date,
        end_date=final_end_date,
        word_frequency_json=json.dumps(frequency_data)
    )
    
    # Many-to-Many 관계 설정 (어떤 신문사가 사용되었는지 기록)  
    result_obj.included_publishers.set(publishers_to_log)
    
    print(f">> WordCloud 가중치 결과 저장 완료. ID: {result_obj.id}. 기간: {final_start_date} ~ {final_end_date}")
    return result_obj

# 사용 예시 (특정 신문사 1, 2, 3으로 2025-09-01부터 2025-09-30까지 실행)
# generate_word_frequencies(date(2025, 9, 1), date(2025, 9, 30), [1, 2, 3])