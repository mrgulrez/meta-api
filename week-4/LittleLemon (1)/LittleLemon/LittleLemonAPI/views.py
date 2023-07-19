import datetime
from django.shortcuts import get_object_or_404, render, get_list_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth.models import User, Group
from rest_framework import status 
from .models import MenuItem, Category, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .helpers import user_in_group, CustomPagination
# Create your views here.
# class MenuItemsView():
#     pass

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def delivery_crew(request):
    if user_in_group(request.user, 'Manager'):
        if request.method == 'GET':
            delivery_crew = Group.objects.get(name = 'Delivery Crew') 
            users = delivery_crew.user_set.all().values('id','username')
            return Response(users, status.HTTP_200_OK)
        if request.method == 'POST' :
            username = request.data['username']
            if username:
                user = get_object_or_404(User, username=username)
                delivery_crew = Group.objects.get(name = "Delivery Crew")
                delivery_crew.user_set.add(user)
                return Response({'message': 'Added'}, status.HTTP_200_OK)
    return Response('Only Managers can add or see Delivery Crew', status.HTTP_401_UNAUTHORIZED)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_delivery_crew(request, userId):
    if user_in_group(request.user, 'Manager'):
        user = get_object_or_404(User, id=userId)
        delivery_crew = Group.objects.get(name = "Delivery Crew")
        delivery_crew.user_set.remove(user)
        return Response({'message': 'deleted'}, status.HTTP_200_OK)
    return Response('Only Managers can delete Delivery Crew', status.HTTP_403_FORBIDDEN)

@api_view(['POST', 'GET'])
@permission_classes([IsAdminUser])
def managers(request):
    if request.method == 'GET':
        managers = Group.objects.get(name = 'Manager') 
        users = managers.user_set.all().values('id','username')
        return Response(users, status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST' :
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name = "Manager")
            managers.user_set.add(user)
            return Response({'message': 'Added'}, status.HTTP_200_OK)
    
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_manager(request, userId):
    user = get_object_or_404(User, id=userId)
    managers = Group.objects.get(name = "Manager")
    managers.user_set.remove(user)
    return Response({'message': 'deleted'}, status.HTTP_200_OK)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def categories(request):
    if(request.method == 'GET'):
        categories = Category.objects.all()
        serialized_categories = CategorySerializer(categories, many=True)
        return Response(serialized_categories.data, status.HTTP_200_OK)
    
    elif request.method == 'POST' and request.user.is_superuser :
        serialized_category = CategorySerializer(data = request.data)
        if serialized_category.is_valid():
            serialized_category.save()
            return Response(serialized_category.data, status.HTTP_201_CREATED)
        return Response(serialized_category.errors, status.HTTP_400_BAD_REQUEST)
    
    return Response({"message":'Only Admin can add a new Category'}, status.HTTP_401_UNAUTHORIZED)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def menu_item(request):
    if(request.method=='GET'):
        paginator = CustomPagination()
        items = MenuItem.objects.all()
        category_slug = request.query_params.get('category')
        sort_by = request.query_params.get('sort_by')
        if category_slug:
            items = items.filter(category__slug = category_slug)
        if sort_by:
            items = items.order_by(sort_by)
        paginated_queryset = paginator.paginate_queryset(items, request)
        serializer = MenuItemSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    elif(request.method=='POST'):
        if request.user.is_superuser:
            serialized_item = MenuItemSerializer(data = request.data)
            if serialized_item.is_valid():
                serialized_item.save()
                return Response(serialized_item.data, status.HTTP_201_CREATED)
            return Response(serialized_item.errors, status.HTTP_404_NOT_FOUND)
        
        return Response({"message":"Only Admin can add Menu Items."},status.HTTP_403_FORBIDDEN)
        
@api_view(['GET','PUT', 'PATCH','DELETE'])
@permission_classes([IsAuthenticated])
def single_menu_item(request, menuItemId):
    try:
        item = MenuItem.objects.get(id=menuItemId)
    except MenuItem.DoesNotExist:
        return Response({"message":'Menu item does not exist'}, status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = MenuItemSerializer(item , many = False)
        return Response(serializer.data, status.HTTP_200_OK)
    
    if user_in_group(request.user, "Manager"):
        if request.method == 'PUT':
            serializer = MenuItemSerializer(item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_200_OK)
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'PATCH':
            serializer = MenuItemSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_200_OK)
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            item.delete()
            return Response('Deleted Successfully', status.HTTP_200_OK)
    return Response({"message":"Only Managers can change menu items."}, status.HTTP_403_FORBIDDEN)


@api_view(['GET','POST','DELETE'])
@permission_classes([IsAuthenticated])
def cart(request):
    if request.method == "GET":
        cart = Cart.objects.filter(user = request.user)
        serialized_cart = CartSerializer(cart, many=True)
        if serialized_cart.data == []:
            return Response({'message':"cart is empty."}, status.HTTP_200_OK)
        return Response(serialized_cart.data, status.HTTP_200_OK)
    if request.method == 'POST':
        menuitem = MenuItem.objects.get(id = request.data['menuitem_id'])
        if Cart.objects.filter(menuitem= menuitem, user = request.user).exists():
            return Response({'message':"Menu item already exists in cart"}, status.HTTP_400_BAD_REQUEST)
        serialized_cart = CartSerializer( data = request.data)
        if serialized_cart.is_valid():
            serialized_cart.validated_data['user'] = request.user
            serialized_cart.save()
            return Response(serialized_cart.data, status.HTTP_201_CREATED)
        return Response(serialized_cart.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        cart = Cart.objects.filter(user = request.user).delete()
        return Response({'message':"Cart is now empty"}, status.HTTP_200_OK)
    
@api_view(['GET','POST','DELETE'])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAuthenticated])
def orders(request):
    if request.method == 'GET':
        if user_in_group(request.user, "Manager") or request.user.is_superuser: 
            paginator = CustomPagination()
            orders = Order.objects.all()
            sort_by = request.query_params.get('sort_by')
            if sort_by:
                orders = orders.order_by(sort_by)
            paginated_queryset = paginator.paginate_queryset(orders, request)
            serializer = MenuItemSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        elif user_in_group(request.user, "Delivery Crew"):
            orders = Order.objects.filter(delivery_crew = request.user)
            status = request.query_params.get('status')
            if status:
                orders = orders.filter(status)
            serialized_orders = OrderSerializer(orders, many = True)
            return Response(serialized_orders.data, status.HTTP_200_OK)
        
        orders = Order.objects.filter(user = request.user)
        status = request.query_params.get('status')
        if status:
            orders = orders.filter(status)
        serialized_orders = OrderSerializer(orders, many = True)
        return Response(serialized_orders.data, status.HTTP_200_OK)
    
    elif request.method == 'POST':
        if user_in_group(request.user, "Manager") or request.user.is_superuser or user_in_group(request.user, "Delivery Crew"):
            return Response({'message': "Only Customers can create Orders"}, status.HTTP_403_FORBIDDEN)
        
        cart_items = Cart.objects.filter(user=request.user)
        if cart_items.exists():
            order = Order.objects.create(user=request.user, total=0, date=datetime.date.today())
            order_total = 0
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    menuitem=cart_item.menuitem,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    price=cart_item.price
                )
                order_total += cart_item.price  

            order.total = order_total 
            order.save()

            cart_items.delete()

            return Response(OrderSerializer(order).data, status.HTTP_200_OK)
        else:
            return Response({'error': 'No cart items found for the user.'}, status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET','PATCH','DELETE'])
@permission_classes([IsAuthenticated])
def single_order(request, orderId):
    try:
        order = Order.objects.get(id=orderId)
    except Order.DoesNotExist:
        return Response('No order for current User is present')
    
    if request.method == "GET" and order.user == request.user:
        order_items = OrderItem.objects.filter(order=order)
        serialized_order_items = OrderItemSerializer(order_items,many=True)
        return Response(serialized_order_items.data, status.HTTP_200_OK)
    
    elif request.method == 'PATCH':
        order = Order.objects.get(id=orderId)
        if user_in_group(request.user, 'Manager'):
            try:
                delivery_crew = User.objects.get(id=request.data['delivery_crew_id'])
            except User.DoesNotExist:
                return Response({'message':'User not Found'}, status.HTTP_404_NOT_FOUND)
            order.delivery_crew = delivery_crew
            order.save()
            return Response({"message":"Delivery person added."})
        
        elif(order.delivery_crew == request.user):
            serialized_order = OrderSerializer(order, data=request.data, partial=True)
            if serialized_order.is_valid():
                serialized_order.save()
                return Response({"message":"Status updated."}, status.HTTP_200_OK)
            else:
                return Response({'message':'Invalid status'}, status.HTTP_400_BAD_REQUEST)
                   
        return Response({"message":"User not authorized for this action"}, status.HTTP_401_UNAUTHORIZED)
    
    elif request.method == "DELETE" and user_in_group(request.user, "Manager"):
        order = Order.objects.get(id=orderId)
        order.delete()
        return Response({"message":"Order Deleted Successfully"}, status.HTTP_200_OK)
    
    return Response({"message":"User not authorized for this action"}, status.HTTP_401_UNAUTHORIZED)
    
                