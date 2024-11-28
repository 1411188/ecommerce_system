from django.shortcuts import render, get_object_or_404
from .models import Product, Cart, CartItem, Order, Message, Rating
from .forms import CartItemForm, OrderForm, RatingForm, FollowForm
from django.core.mail import send_mail
from django.contrib import messages, message

def add_to_cart(request, product_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()
    return render(request, 'shop/cart.html', {'cart': cart})

def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'shop/cart.html', {'cart': cart})

def place_order(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    for item in cart.cartitem_set.all():
        Order.objects.create(
            user=request.user,
            product=item.product,
            quantity=item.quantity,
            total_price=item.quantity * item.product.price
        )
    cart.cartitem_set.clear()
    return render(request, 'shop/oredr_confirmation.html')

def inbox(request):
    messgaes = Message.objects.filter(user=request.user).order_by('-craeted_at')
    return render(request, 'shop/inbox.html', {'messages': messages})

def rate_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        rating = request.POST['rating']
        comment = request.POST['comment']
        Rating.objects.cretae(user=request.user, product=product, rating=rating, comment=comment)
        return render(request, 'shop/product_detail.html', {'product': product})

def update_product_price(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == 'POST':
        new_price = request.POST['price']
        product.price = new_price
        product.save()
    return render(request, 'shop/product_update.html', {'product': product})

def send_receipt(order):
    subject = 'Your Order Receipt'
    messgae = f'Order ID: {order.id}\nProduct: {order.product.name}\nTotal: {order.total_price}'
    send_mail(subject, message, 'from@example.com', [order.user.email])

def place_order(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    for item in cart.cartitem_set.all():
        order = Order.objects.create(
            user=request.user,
            product=item.product,
            quantity=item.quantity,
            total_price=item.quantity * item.product.price
        )
    send_receipt(order)
    cart.cartitem_set.clear()
    return render(request, 'shop/order_confirmation.html')
