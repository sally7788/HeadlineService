from django.shortcuts import render
from .serializers import *
from rest_framework import generics
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


class HeadlineDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Headline.objects.all()
    serializer_class = HeadlineSerializer
