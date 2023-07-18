from rest_framework import generics
from .serializers import MenuItemSerializer, CategorySerializer
from .models import MenuItem, Category
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'inventory']
    filterset_fields = ['price', 'inventory']
    search_fields = ['category']

@api_view()
@permission_classes([IsAuthenticated()])
def secret(request):
    return Response({"message": "Some secret message"})
