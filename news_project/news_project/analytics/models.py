from django.db import models

class Publisher(models.Model):
    id = models.SmallAutoField(primary_key=True, verbose_name="발행처 고유 ID")
    
    # 요청: UNIQUE, NOT NULL
    name = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="발행처 이름"
    )
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "발행처"
        verbose_name_plural = "발행처 목록"

class News(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="뉴스 고유 ID")
    
    publisher = models.ForeignKey(
        Publisher, 
        on_delete=models.CASCADE,
        related_name='headlines',
        verbose_name="발행처"
    )
    # 요청: NOT NULL
    title = models.CharField(max_length=500, verbose_name="뉴스 제목")
    url = models.URLField(max_length=500, unique=True, verbose_name="원본 URL")
    
    # 요청: NOT NULL
    published_date = models.DateField(verbose_name="발행 날짜")
    
    # 요청: FOREIGN KEY, NOT NULL
    view_count = models.IntegerField(
        default=0, 
        null=True, 
        blank=True,
        verbose_name="조회수"       
    )
    
    # 요청: DEFAULT 0
    crawled_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="최종 크롤링 시점"
    )

    def __str__(self):
        return self.title[:50] + '...' if len(self.title) > 50 else self.title

    class Meta:
        verbose_name = "뉴스"
        verbose_name_plural = "뉴스 목록"
        indexes = [
            models.Index(fields=['published_date']),
            models.Index(fields=['publisher']),
        ]
        
class WordCloudResult(models.Model):
  
    # Many-to-Many 관계: Publisher 모델 참조로 변경
    included_publishers = models.ManyToManyField(
        Publisher, 
        related_name='wordcloud_results',
        verbose_name="포함된 발행처 목록"
    )
    
    # 사용된 기간 (날짜가 선택되지 않았을 경우, 실제 데이터의 min/max 날짜가 저장됨)
    start_date = models.DateField(verbose_name="집계 시작일")
    end_date = models.DateField(verbose_name="집계 종료일")
    
    # 워드클라우드 빈도수 데이터 (JSON 형태)
    word_frequency_json = models.JSONField(verbose_name="빈도수 JSON 데이터")
    
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="결과 생성 시각"
    )
    
    # 워드클라우드 이미지 경로 (이미지 저장을 안하지만, 필드는 확장성 때문에 남겨둠)
    image_path = models.CharField(
        max_length=500, 
        blank=True, 
        null=True,
        verbose_name="이미지 파일 경로"
    )
    
    def __str__(self):
        return f"WC Result: {self.start_date} ~ {self.end_date}"

    class Meta:
        verbose_name = "워드클라우드 결과"
        verbose_name_plural = "워드클라우드 결과 목록"