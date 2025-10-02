from django.http import HttpResponseRedirect
from .serializers import *
from rest_framework import generics, status
from rest_framework.response import Response
from django.http import JsonResponse
from django.db.models import Count
from .models import *
from .data_processing.wordcloud_generator import generate_word_frequencies

# Create your views here.


class PublisherList(generics.ListCreateAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class PublisherDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class HeadlineList(generics.ListCreateAPIView):
    queryset = Headline.objects.all()
    serializer_class = HeadlineSerializer

    def post(self, request, *args, **kwargs):
        title = request.data.get('title')

        if self.queryset.filter(title=title).exists():
            instance = Headline.objects.get(title=title)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return self.create(request, *args, **kwargs)


class DeletePublisher(generics.RetrieveDestroyAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    

class HeadlineDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Headline.objects.all()
    serializer_class = HeadlineSerializer

def get_wordcloud_data(request):
    
    #사용자 요청 파라미터 가져오기 
    start_date_req = request.GET.get('start_date')
    end_date_req = request.GET.get('end_date')
    
    
    publishers_param= request.GET.get('publishers', '') 
    publisher_ids_req = []

    if publishers_param:
        # URL에 publishers 값이 있으면 해당 ID만 사용
        try:
            publisher_ids_req = [int(p_id) for p_id in publishers_param.split(',')]
        except ValueError:
            return JsonResponse({'status': 'error', 'message': '유효하지 않은 발행처 ID입니다.'}, status=400)
    else:
        # URL에 publishers 값이 없으면 DB에 있는 모든 발행처 ID를 가져옴
        publisher_ids_req = list(Publisher.objects.values_list('id', flat=True))
        
    #캐싱된 결과 조회 
    latest_cached=None
    
    cached_results=WordCloudResult.objects.filter(
        start_date=start_date_req,
        end_date=end_date_req,
    ).annotate(p_count=Count('included_publishers') #언론사 총 개수 
    ).filter(p_count=len(publisher_ids_req)) # 연결된 언론사 수 = 요청된 발행사 수 
    
    #언론사 id 모두 포함하는지 
    for pub_id in publisher_ids_req:
        cached_results=cached_results.filter(included_publishers__id=pub_id)
    latest_cached=cached_results.order_by('-created_at').first()
    
    #캐싱된 결과가 있으면 해당 결과 반환
    if latest_cached:
        print(">> 캐싱된 워드클라우드 결과를 반환합니다.")
        return JsonResponse({
            'status': 'success',
            'result_id': latest_cached.id,
            'data': latest_cached.word_frequency_json
        })
    else:
        print(">> 캐싱된 결과가 없습니다. 새로운 워드클라우드 생성 작업을 시작합니다.")
        
        result=generate_word_frequencies(
            start_date=start_date_req,
            end_date=end_date_req,
            selected_publisher_ids=publisher_ids_req
        )
        if result is None:
            return JsonResponse({'status': 'error', 'message': '워드클라우드 생성에 실패했습니다. 조건에 맞는 기사가 없습니다.'}, status=500)
        else:
            return JsonResponse({
                'status': 'success',
                'result_id': result.id,
                'data': result.word_frequency_json
            })




