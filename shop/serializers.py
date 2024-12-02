from rest_framework import serializers
from .models import Product, Cart, CartItem, Order, Message, Rating
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProductSerializer(serializers.ModelSerializer):
    seller = SellerSerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'created_at', 'seller']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    products = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'products']


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    product = ProductSerializer()

    class Meta:
        model = Order
        fields = ['id', 'user', 'product', 'quantity', 'total_price', 'ordered_at']


class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Message
        fields = ['id', 'user', 'content', 'is_alert', 'created_at']


class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    product = ProductSerializer()

    class Meta:
        model = Rating
        fields = ['id', 'user', 'product', 'rating', 'comment', 'created_at']


