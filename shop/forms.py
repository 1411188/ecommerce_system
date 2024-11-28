from django import forms
from .models import CartItem, Order, Rating, Follow

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']
        
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'quantity', 'total_price']
        
class RatingForm(forms.ModelForm):
    class Meta:
    model = Rtaing
    fields = ['product', 'rating', 'comment']
    
class FollowForm(forms.ModelForm):
    class Meta:
        model = Folllow
        fields = ['seller']
