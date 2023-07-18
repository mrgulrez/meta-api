from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .serializers import RatingSerializer, Rating

# Create your views here.
class RatingsView(generics.ListCreateAPIView):
    serializer_class = RatingSerializer
    queryset = Rating.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsAuthenticated()]
