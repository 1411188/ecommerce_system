from django.urls import path, include
from rest_framework.routers import DefaultRouter
from. import views
from . views import *

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', login_user, name='login_user'),
    path('dashboard/', dashboard, name='dashboard'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('cart/view/', views.view_cart, name='view_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/', views.add_to_cart, name='remove_from_cart'),
    path('order/place/', views.place_order, name='place_order'),
    path('inbox/', views.inbox, name='inbox'),
    path('product/<init:pk/update-price/', views.update_product_price, name=update_product_price),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/rate/', views.rate_product, name='rate_product'),
    path('receipts/', views.receipt_list, name='receipt_list'),
    path('receipts/<str:receipt_number>/', views.receipt_detail, name='receipt_detail'),
    path('receipts/<str:receipt_number>/download/', views.download_receipt, name='download_receipt'),
    path('payment/stripe/', views.process_stripe_payment, name='process_stripe_payment'),
    path('api/products/', views.product_list, name='product_list'),
    path('webhook/', stripe_webhook, name='stripe-webhook'),
]
