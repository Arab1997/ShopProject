import datetime
import hashlib
import json
import logging

import requests
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from payme.methods.generate_link import GeneratePayLink
from payme.views import MerchantAPIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.models import CartItem
from store.models import Product
from .forms import OrderForm
from .models import Order
from .models import Payment, OrderProduct
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status



def payment_view(request, order_id):
    # Order va to'lov miqdorini olish (bu faqat misol, realdagi kod boshqa bo'lishi mumkin)
    order = Order.objects.get(id=order_id)
    amount = order.amount

    # To'lov linkini olish
    pay_link = GeneratePayLink(order_id=order_id, amount=amount).generate_link()

    return render(request, 'payments.html', {
        'order': order,
        'amount': amount,
        'pay_link': pay_link
    })

@csrf_exempt
def payme_payment(request):
    if request.method == "POST":
        order_id = request.POST.get('order_id')
        amount = request.POST.get('amount')

        # Payme.uz tomonidan talab qilingan sha256 hashingni yaratish
        merchant_key = settings.PAYME_MERCHANT_KEY
        token = hashlib.sha256((order_id + amount + merchant_key).encode('utf-8')).hexdigest()

        # To'lov ma'lumotlari
        data = {
            "amount": amount,
            "order_id": order_id,
            "merchant_id": settings.PAYME_MERCHANT_ID,
            "token": token,
        }

        # To'lov so'rovini amalga oshiring
        return JsonResponse(data)
    return JsonResponse({'error': 'Only POST method is allowed'})

@csrf_exempt
def payment_callback(request):
    if request.method == 'POST':
        # Payme.uz'dan kelgan ma'lumotlarni olish
        data = request.POST
        order_id = data.get('order_id')
        status = data.get('status')

        # Buyurtmani yangilash
        try:
            order = Order.objects.get(order_id=order_id)
            if status == 'completed':
                order.status = 'completed'
                order.save()
                return HttpResponse('To\'lov muvaffaqiyatli amalga oshirildi!')
            else:
                return HttpResponse('To\'lov amalga oshirilmadi.')
        except Order.DoesNotExist:
            return HttpResponse('Buyurtma topilmadi.')
    else:
        return HttpResponse('No POST data received.')


class PaymeCallBackAPIView(MerchantAPIView):
    def create_transaction(self, order_id, action, *args, **kwargs) -> None:
        print(f"create_transaction for order_id: {order_id}, response: {action}")

    def perform_transaction(self, order_id, action, *args, **kwargs) -> None:
        print(f"perform_transaction for order_id: {order_id}, response: {action}")

    def cancel_transaction(self, order_id, action, *args, **kwargs) -> None:
        print(f"cancel_transaction for order_id: {order_id}, response: {action}")


class GeneratePayLinkSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    amount = serializers.IntegerField()


class GeneratePayLinkAPIView(APIView):
    def post(self, request, *args, **kwargs):
        """
        Generate a payment link for the given order ID and amount.

        Request parameters:
            - order_id (int): The ID of the order to generate a payment link for.
            - amount (int): The amount of the payment.

        Example request:
            curl -X POST \
                'http://your-host/shop/pay-link/' \
                --header 'Content-Type: application/json' \
                --data-raw '{
                "order_id": 999,
                "amount": 999
            }'

        Example response:
            {
                "pay_link": "http://payme-api-gateway.uz/bT0jcmJmZk1vNVJPQFFoP05GcHJtWnNHeH"
            }
        """
        serializer = GeneratePayLinkSerializer(
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )
        try:
            pay_link = GeneratePayLink(**serializer.validated_data).generate_link()
            return Response({"pay_link": pay_link}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GeneratePayLink:
    def __init__(self, order_id, amount):
        self.order_id = order_id
        self.amount = amount

    def generate_link(self):
        payload = {
            'merchant_id': settings.PAYME_MERCHANT_ID,
            'order_id': self.order_id,
            'amount': self.amount,
            'return_url': 'http://127.0.0.1:8000/payment-return/',
            'callback_url': 'https://8d82-82-215-100-34.ngrok-free.app/payment-callback/',

        }
        try:
            response = requests.post(f'{settings.PAYME_URL}/create', json=payload)
            response.raise_for_status()  # Raises an error for 4XX/5XX responses

            print("Response Text:", response.text)

            # Safely attempt to parse JSON response
            result = response.json()
            if result.get('status') == 'success':
                return result.get('pay_link')
            else:
                raise Exception(result.get('message', 'Failed to generate payment link'))
        except requests.exceptions.RequestException as e:
            raise Exception(f'Error communicating with Payme: {e}')
        except json.JSONDecodeError as e:
            raise Exception(f'Invalid JSON response from Payme: {e}')


def payments(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body.decode('utf-8'))

            # Extract relevant data
            order_id = data.get('orderID')
            trans_id = data.get('transID')
            payment_method = data.get('payment_method')
            status = data.get('status')

            # Process payment here

            # Return a JSON response
            return JsonResponse({'status': 'success', 'order_id': order_id, 'transID': trans_id})
        except json.JSONDecodeError as e:
            # Handle JSON decode error
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def payments(request):
    body = json.loads(request.body)
    print(body)
    order = Order.objects.get(user=request.user, is_ordered=False, amount=body['amount'], order_id=body['order_id'])

    # Store transaction details inside Payment model
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.amount,
        order_id=order.order_id,
        status=body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_id': order.order_id,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)


def place_order(request, total=0, quantity=0, ):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    amount = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    amount = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.amount = amount
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # 20210305
            order_id = current_date + str(data.id)
            data.order_id = order_id
            data.save()

            order_id = Order.objects.get(user=current_user, is_ordered=False, order_id=order_id)
            context = {
                'order_id': order_id,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'amount': amount,
                'callback_url': 'https://64e4-82-215-100-34.ngrok-free.app/payments/merchant/',
                # Replace with your callback URL

            }

            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


def order_complete(request):
    order_id = request.GET.get('order_id')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_id=order_id, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_id': order.order_id,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
