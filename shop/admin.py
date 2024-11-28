from django.contrib import admin
from .models import Product, Cart, Order, CartItem, Message, Rating

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(CartItem)
admin.site.register(Message)
admin.site.register(Rating)
