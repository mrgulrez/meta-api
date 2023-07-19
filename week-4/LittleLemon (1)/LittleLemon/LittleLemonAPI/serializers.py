from .models import MenuItem,Category, Cart, Order, OrderItem
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only= True)
    category_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = MenuItem
        fields =['id','title', 'price', 'featured', 'category', 'category_id']

class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only = True)
    menuitem_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Cart
        fields = ['menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']

    def create(self, validated_data):
    # Check if a model instance with the same unique constraint exists
        menuitem = validated_data.get('menuitem')
        user = validated_data.get('user')
        if Cart.objects.filter(menuitem=menuitem, user = user).exists():
            raise serializers.ValidationError('Model with the same unique constraint already exists.')

        # Create the model instance
        instance = Cart.objects.create(**validated_data)
        return instance
    
class OrderSerializer(serializers.ModelSerializer):
    delivery_crew = UserSerializer(read_only = True)
    user = UserSerializer(read_only = True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']
    
class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only = True)
    menuitem_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = OrderItem
        fields = ['menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']
