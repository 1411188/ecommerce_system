from django.urls import path
from. import views
from . views import update_product_price

urlpatterns = [
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('order/place/', views.place_order, name='place_order'),
    path('inbox/', views.inbox, name='inbox'),
    path('product/updtae/<int:product_id>/', views.update_product_price, name=update_product_price),
    path('seller/follow/<int:seller_id>/', views.follow_seller, name='follow_seller',)
]
