from django.shortcuts import render
from rest_framework import viewsets
from .serializers import MenuItemSerializer,CategorySerializer
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.contrib.auth.models import Group
from rest_framework.response import Response
from .models import MenuItem,  Category,Cart
from .serializers import MenuItemSerializer,CartSerializer
from django.shortcuts import get_object_or_404
from .permissions import IsManagerOrReadOnly 
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .models import OrderItem,Order
from .serializers import OrderSerializer






#all menu items list with added permissions 
class MenuItemsView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = MenuItemSerializer
    filterset_fields = ['price', 'category']
    search_fields = ['title']
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]

#single menu item list 
class SingleMenuItemView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]


class CategoriesView(viewsets.ModelViewSet):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


#assign a group to users only authenticated managers could perform this
class UserGroupAssignView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, user_id):
        if not request.user.groups.filter(name='managers').exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        group_name = request.data.get('group_name')
        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(name=group_name)
        except (User.DoesNotExist, Group.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)
        user.groups.add(group)
        user.save()
        return Response(status=status.HTTP_200_OK)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def order_list(request):
    if request.method == 'GET':
        user = request.user
        group_names = user.groups.values_list('name', flat=True)
        orders = Order.objects.all()
       
        sttus = request.query_params.get('status', None)
        if sttus:
            orders = Order.objects.filter(status=sttus)
        else:
            orders = Order.objects.all()
        
        if 'managers' in group_names:
            serializer = OrderSerializer(orders, many=True)
       
        elif 'delivery crew' in group_names:
            orders = orders.filter(delivery_crew=user)
            serializer = OrderSerializer(orders, many=True)
        
        else:
            orders = orders.filter(user=user)
            serializer = OrderSerializer(orders, many=True)
        
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            # Get the User instance from the request data
            user = User.objects.get(id=request.data['user'])
            
            # Create the Order object
            order = Order.objects.create(user=user,
                                        delivery_crew=request.data.get('delivery_crew'),
                                        status=request.data.get('status'),
                                        total=request.data.get('total'),
                                        date=request.data.get('date'))
            
            # Create the OrderItem objects
            order_items = []
           
            for item in request.data['orderitem_set']:
                menuitem = MenuItem.objects.get(id=item['menuitem'])
                order_item = OrderItem(order=order, menuitem=menuitem, quantity=item['quantity'],
                                    unit_price=item['unit_price'], price=item['price'])
                order_items.append(order_item)
            OrderItem.objects.bulk_create(order_items)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, pk):
    order = get_object_or_404(Order, id=pk)
    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Get the menu item from the request data
    try:
        menu_item = MenuItem.objects.get(id=request.data['menu_item'])
    except MenuItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Create the cart item
    cart_item = Cart(user=user,
                     menuitem=menu_item,
                     quantity=request.data.get('quantity', 1),
                     unit_price=menu_item.price,
                     price=menu_item.price * request.data.get('quantity', 1))
    cart_item.save()

    serializer = CartSerializer(cart_item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def flush_cart(request, user_id):
    try:
        # Get the cart items associated with the user
        cart_items = Cart.objects.filter(user_id=user_id)

        # Delete all the cart items
        cart_items.delete()

        # Return a success response
        return Response({"message": "Cart flushed successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Cart.DoesNotExist:
        # Return a failure response if the user does not have any cart items
        return Response({"message": "User does not have any cart items."}, status=status.HTTP_404_NOT_FOUND)