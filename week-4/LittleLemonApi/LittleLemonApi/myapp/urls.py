from django.urls import path
from . import views
from .views import UserGroupAssignView,order_list,order_detail,add_to_cart,SingleMenuItemView,MenuItemsView



menu_item_list = MenuItemsView.as_view({
    'get': 'list',
    'post': 'create'
})
menu_item_detail = SingleMenuItemView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('menu-items', menu_item_list),
    path('categories', views.CategoriesView.as_view({'get': 'list'} )),
    path('menu-items/<int:pk>', menu_item_detail),
    path('users/<int:user_id>/groups/', UserGroupAssignView.as_view()),
    path('orders/', order_list),
    path('orders/<int:pk>/', order_detail),
    path('users/<int:user_id>/cart/menu-items/', add_to_cart),
    path('users/<int:user_id>/cart/flush/', views.flush_cart),
]