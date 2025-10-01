from django.shortcuts import render
from .serializers import *
from rest_framework import generics
from rest_framework.response import Response

# Create your views here.

class PublisherList(generics.ListCreateAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer

class NewsList(generics.ListCreateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer

class DeletePublisher(generics.RetrieveDestroyAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer