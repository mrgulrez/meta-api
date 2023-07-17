from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView

# Create your views here.
@api_view(['GET', 'POST'])
def books(request):
    return Response('list of the books',
                     status=status.HTTP_200_OK)

class BookList(APIView):
    def post(self, request):
        return Response({"title":request.data.get('title')}, status= status.HTTP_200_OK)
        # return Response({"message": "Creating a book"}, status=status.HTTP_201_CREATED)

    def get(self, request, pk=None):
        author = request.GET.get('author')
        if author:
            return Response({"message": "Displaying a book " + author}, status=status.HTTP_200_OK)


	# def destroy(self, request, pk=None):
	# 	return Response({"message":"Deleting a book"}, status.HTTP_200_OK)

	# def partial_update(self, request, pk = None):
	# 	return Response({"message":"Partially updating a book"}, status.HTTP_200_OK)

	

	# def update(self, request):
	# 	return Response({"message":"Updating a book"}, status.HTTP_200_OK)
	
	# def list(self, request):
	# 	return Response({"message":"All books"}, status.HTTP_200_OK)


class Book(APIView):
    def get(self, request, pk):
        return Response({'message': "single book id " + str(pk)}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        return Response({"title": request.data.get('title')}, status=status.HTTP_200_OK)