from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from django.contrib import admin

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=100)

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product =models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Calculate total_price based on product price and quantity
        if self.product and self.quantity:
            self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order by {self.user.username} for {self.quantity} {self.product.name}(s)"

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_alert = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)

def follw_seller(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)
    Follow.objects.create(user=request.user, seller=seller)
    return render(request, 'shop/seller_detail.html', {'seller': seller})


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'seller')
    search_fields = ('name', 'description')


class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    search_fields = ('cart__user__username', 'product__name')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'total_price', 'is_completed')
    search_fields = ('user__username',)
    list_filter = ('is_completed',)

class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating')
    search_fields = ('user__username', 'product__name')
    list_filter = ('rating',)
    
class Receipt(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    receipt_number = models.CharField(max_length=100, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Receipt {self.receipt_number}"
    
