from django.contrib import admin
from django.urls import  path
from . import views
urlpatterns = [
    path('groups/manager/users/', views.managers),
    path('groups/manager/users/<int:userId>', views.delete_manager),
    path('groups/delivery-crew/users/', views.delivery_crew),
    path('groups/delivery-crew/users/<int:userId>', views.delete_delivery_crew),
    path('categories/', views.categories),
    path('menu-items/', views.menu_item),
    path('menu-items/<int:menuItemId>/', views.single_menu_item),
    path('cart/menu-items/', views.cart),
    path('orders/', views.orders),
    path('orders/<int:orderId>/', views.single_order),
]