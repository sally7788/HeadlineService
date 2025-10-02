from django.contrib import admin

from django.contrib import admin
from .models import Publisher, News, WordCloudResult

# Django Admin 커스터마이징을 위한 데ко레이터 방식(@admin.register)을 사용하면 더 깔끔합니다.

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """ Publisher 모델을 위한 관리자 설정 """
    list_display = ('id', 'name')  # 목록에 id와 name 필드를 표시
    search_fields = ('name',)      # name 필드로 검색 기능 추가


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """ News 모델을 위한 관리자 설정 """
    list_display = ('id', 'title', 'get_publisher_name', 'published_date', 'view_count') # 목록에 표시할 필드
    list_filter = ('published_date', 'publisher_id__name') # 발행일과 발행처 이름으로 필터 기능 추가
    search_fields = ('title',)  # 제목으로 검색 기능 추가
    date_hierarchy = 'published_date' # 발행일 기준으로 날짜 네비게이션 추가 (상단에 연/월/일 링크 생성)
    ordering = ('-published_date',) # 발행일 최신순으로 기본 정렬

    # ForeignKey 필드의 이름을 더 명확하게 보여주기 위한 함수
    @admin.display(description='발행처')
    def get_publisher_name(self, obj):
        return obj.publisher_id.name


@admin.register(WordCloudResult)
class WordCloudResultAdmin(admin.ModelAdmin):
    """ WordCloudResult 모델을 위한 관리자 설정 """
    list_display = ('id', 'start_date', 'end_date', 'created_at') # 목록에 표시할 필드
    list_filter = ('start_date', 'end_date') # 시작일과 종료일로 필터 기능 추가
    readonly_fields = ('created_at', 'word_frequency_json') # 생성시각과 JSON 데이터는 수정 불가하도록 설정
    filter_horizontal = ('included_publishers',) # ManyToManyField를 편하게 선택할 수 있는 UI로 변경