from rest_framework import serializers
from decimal import Decimal
from .models import Category,MenuItem,Cart,Order,OrderItem
class CategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','slug','title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'featured', 'price', 'category']
        depth = 1
    def create(self, validated_data):
            category_data = validated_data.pop('category')
            category_serializer = CategorySerializer(data=category_data)
            if category_serializer.is_valid():
                category = category_serializer.save()
                validated_data['category'] = category
                return super().create(validated_data)
            else:
                raise serializers.ValidationError(category_serializer.errors)

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']

class OrderSerializer(serializers.ModelSerializer):
    orderitem_set = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'orderitem_set']
        
    def create(self, validated_data):
        order_items_data = validated_data.pop('orderitem_set')
        order = Order.objects.create(**validated_data)

        for order_item_data in order_items_data:
            OrderItem.objects.create(order=order, **order_item_data)

        return order
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity', 'unit_price', 'price']