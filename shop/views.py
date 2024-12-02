import requests
import stripe
from django.shortcuts import render, get_object_or_404
from .models import Product, Cart, CartItem, Order, Message, Rating, Receipt
from .forms import CartItemForm, OrderForm, RatingForm, FollowForm
from django.core.mail import send_mail
from django.contrib import messages
from django.http import JsonResponse
from  django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.contrib.auth.models import User
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

class CreatePaymentIntentView(View):
    def post(self, request, *args, **kwargs):
        intent = stripe.PaymentIntent.create(
            amount=2000,  # Amount in cents
            currency='usd',
            metadata={'integration_check': 'accept_a_payment'},
        )
        return JsonResponse({
            'client_secret': intent.client_secret
        })

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print('PaymentIntent was successful!')

    return JsonResponse({'status': 'success'})
    
def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("User registered successfully!")
    else:
        form = UserRegistrationForm()
    return render(request, 'shop/register_user.html', {'form': form})
    
def dashboard(request):
    user = request.user
    cart = Cart.objects.filter(user=user).first()
    orders = Order.objects.filter(user=user)
    messages = Message.objects.filter(user=user)
    rates = Rate.objects.filter(user=user)
    context = {
        'cart': cart,
        'orders': orders,
        'messages': messages,
        'rates': rates,
    }
    return render(request, 'shop/dashboard.html', context)
    
def add_to_cart(request, product_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()
    return render(request, 'shop/cart.html', {'cart': cart})

def remove_from_cart(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()  # Remove the item completely if quantity is 0
    except CartItem.DoesNotExist:
        # Handle the case where the cart item does not exist
        pass

    return redirect('cart')  # Redirect to the cart page
    
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
        
def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})
    
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


def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Optionally, add items back to the cart
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=order.product)
    cart_item.quantity += order.quantity
    cart_item.save()
    
    # Delete the order
    order.delete()

    return redirect('order_history')
    
def receipt_list(request):
    receipts = Receipt.objects.filter(user=request.user).order_by('-transaction_date')
    return render(request, 'receipts/receipt_list.html', {'receipts': receipts})

def receipt_detail(request, receipt_id):
    # Fetch the receipt from the database
    receipt = Receipt.objects.get(id=receipt_id)
    return render(request, 'shop/receipt_detail.html', {'receipt': receipt})
    
def download_receipt(request, receipt_id):
    receipt = Receipt.objects.get(id=receipt_id)
    
    receipt_content = f"Receipt for order {receipt.id}\nAmount: {receipt.amount}"
    
    response = HttpResponse(receipt_content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="receipt_{receipt_id}.txt"'
    
    return response  
    
@api_view(['POST'])
def login_user(request):
    google_token = request.data.get('google_token')
    username = request.data.get('username')
    password = request.data.get('password')
    
    if google_token:
        google_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {google_token}"}
        response = requests.get(google_url, headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            email = user_data.get("email")
            name = user_data.get("name")
            
            user, created = User.objects.get_or_create(username=email, defaults={"email": email})
            if created:
                user.set_unusable_password()
                user.save()
                
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    "token": token.key,
                    "username": user.username,
                    "email": user.email,
                    "message": "Google login successful" if not created else "Account created with Google login"
                }, status=HTTP_200_OK)
        return Response({"error": "Invalid Google token"}, status=HTTP_400_BAD_REQUEST)
        
    

    elif username and password:
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "message": "Login successful"
            }, status=HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=HTTP_400_BAD_REQUEST)

    # 3. If No Credentials Provided
    return Response({"error": "Invalid request. Provide either Google token or username and password."}, status=HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_to_cart(request):
    user = request.user
    product = request.data.get('product')
    quantity = request.data.get('quantity')
    
    cart, _ = Cart.objects.get_or_create(user=user)
    product = Product.objects.get(name=product)
    cart_item, created = CartItem.objects.get_or_created(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += quantity
    cart_item.save()
    
    return Response({'message': 'Item added to cart'})

@api_view(['POST'])
def remove_from_cart(request):
    user = request.user
    cart = Cart.objects.get(user=user)
    product = request.data.get('product')
    cart_item = CartItem.objects.get(cart=cart, product=product)
    cart_item.delete()
    
    return Response({'message': 'Item removed from cart'})
    
@api_view(['POST'])
def place_order(request):
    user = request.user
    cart = Cart.objects.get(user=user)
    total_price = sum(item.product.price * item.quantity for item in cart.cartitem_set.all())

    for item in cart.cartitem_set.all():
        Order.objects.create(user=user, product=item.product, quantity=item.quantity, total_price=item.product.price * item.quantity)
        item.delete()

    return Response({'message': 'Order placed successfully', 'total_price': total_price})

@api_view(['POST'])
def process_stripe_payment(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    amount = int(request.data.get('amount'))  # in cents
    token = request.data.get('stripeToken')

    try:
        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            description='Payment',
            source=token,
        )
        return Response({'message': 'Payment successful'})
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def rate_product(request, pk):
    user = request.user
    product = Product.objects.get(id=pk)
    rating = request.data.get('rating')
    comment = request.data.get('comment')

    Rating.objects.create(user=user, product=product, rating=rating, comment=comment)
    return Response({'message': 'Product rated successfully'})

@api_view(['PATCH'])
def update_price(request, pk):
    product = Product.objects.get(id=pk)
    new_price = request.data.get('price')
    product.price = new_price
    product.save()

    return Response({'message': 'Price updated successfully'})

@api_view(['GET'])
def receipt_list(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def view_cart(request):
    cart = Cart.objects.get(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)

