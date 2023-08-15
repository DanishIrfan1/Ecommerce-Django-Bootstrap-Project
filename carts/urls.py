from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'), # add_cart/1/ -> 1 is the product_id passed to the view
    path('remove_cart/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'), # remove_cart/1/ -> 1 is the product_id passed to the view
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'), # remove_cart_item/1/ -> 1 is the product_id passed to the view
    path('checkout/', views.checkout, name='checkout'),
]
