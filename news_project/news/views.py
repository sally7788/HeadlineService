from django.http import HttpResponseRedirect
from .serializers import *
from rest_framework import generics, status
from rest_framework.response import Response

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


class HeadlineDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Headline.objects.all()
    serializer_class = HeadlineSerializer
