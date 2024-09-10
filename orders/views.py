import base64
import datetime
import hashlib
import json
import re
from pprint import pprint

import requests
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from payme.methods.generate_link import GeneratePayLink
from payme.views import MerchantAPIView
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.models import CartItem
from store.models import Product
from .forms import OrderForm
from .models import Order
from .models import Payment, OrderProduct

PAYME_API_URL = "https://checkout.paycom.uz/api"  # Payme.uz API endpoint
PAYME_MERCHANT_ID = "66cc53408326c8dc50ac7216"  # Sizning Payme.uz merchant ID

# pay_link = GeneratePayLink(
#     order_id="999",
#     amount=9999,
#     callback_url="https://b4fa-82-215-100-34.ngrok-free.app/payment-callback/"
# ).generate_link()
#
# pprint(pay_link)


# def get_order_details(order_id):
#     # Извлекаем объект заказа из базы данных по его order_id
#     order = get_object_or_404(Order, order_id=order_id)
#
#     # Получаем order_id и amount из объекта заказа
#     order_id_value = order.order_id
#     amount_value = order.amount
#
#     # Используйте order_id и amount в вашем запросе
#     # Например, создайте параметры для API платежной системы
#     payment_data = {
#         "order_id": order_id_value,
#         "amount": amount_value,
#     }
#
#     return payment_data




# https://36d0-82-215-100-34.ngrok-free.app/orders/send-check/?order_id=999&amount=1000
class SendCheckView(View):
    def post(self, request, *args, **kwargs):
        # Параметры для отправки чека
        order_id = request.POST.get('order_id')
        amount = request.POST.get('amount')
        # Формируем URL для запроса
        payme_url = f'{settings.PAYME_URL}/create'

        # Encode credentials properly
        username = '66cc53408326c8dc50ac7216'  # Replace with actual username
        password = 'PS0hbhKTg4DRvTfWhDwKw?nknY6UQxeMkO7r'  # Replace with actual password
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        # Заголовки запроса
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {encoded_credentials}',  # Use encoded credentials
            # 'Authorization': 'Basic UGF5Y29tOnlvdXJfc2VjcmV0X2tleQ==',  # Replace with your actual encoded credentials

        }
        # Параметры для GET-запроса
        params = {
            'm': settings.PAYME_MERCHANT_ID,  # Ваш ID продавца
            'ac.order_id': order_id,  # Уникальный идентификатор заказа
            'a': amount,  # Сумма платежа в тийинах
        }
        try:
            # Выполняем запрос к Payme
            response = requests.get(payme_url, headers=headers, params=params)
            response.raise_for_status()

            # Возвращаем ответ от Payme
            return JsonResponse(response.json(), status=response.status_code)
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)


# def create_payment_request(order_id):
#     # Получаем данные заказа
#     payment_data = get_order_details(order_id)
#
#     # Создаем запрос к платежной системе
#     response = requests.post("https://api.payme.uz/v1/pay", data=payment_data)
#
#     # Обрабатываем ответ
#     if response.status_code == 200:
#         # Успешная обработка
#         return response.json()
#     else:
#         # Обработка ошибки
#         return {"error": "Ошибка платежа"}


# @csrf_exempt
# def process_payment(request):
#     if request.method == 'POST':
#         order_id = request.POST.get('order_id')
#         amount = request.POST.get('amount')
#
#         # Логика для обработки платежа
#         # Пример: отправка данных в платежную систему
#         payment_data = {
#             "order_id": order_id,
#             "amount": amount,
#         }
#
#         # Примерный запрос к платежной системе (должен быть реализован)
#         response = create_payment_request(order_id)
#
#         # Обработка ответа платежной системы
#         if 'error' in response:
#             return render(request, 'error.html', {'error': response['error']})
#         else:
#             return render(request, 'success.html', {'payment_details': response})
#
#     return redirect('home')





# class GeneratePayLink:
#     def __init__(self, order_id, amount):
#         self.order_id = order_id
#         self.amount = amount
#
#     def generate_link(self):
#         payload = {
#             'm': settings.PAYME_MERCHANT_ID,
#             'ac.order_id': self.order_id,
#             'a': self.amount,
#             'c': 'http://127.0.0.1:8000/payment-return/',
#             'callback_url': 'https://36d0-82-215-100-34.ngrok-free.app/payment-callback/',
#         }
#
#         auth_string = f"{settings.PAYME_MERCHANT_ID}:{settings.PAYME_SECRET_KEY}"
#         auth_header = base64.b64encode(auth_string.encode()).decode()
#
#         headers = {
#             'Content-Type': 'application/json',
#             'Authorization': f'Basic UGF5Y29tOlBTMGhiaEtUZzREUnZUZldoRHdLdz9ua25ZNlVReGVNa083cg=='
#             # 'Authorization': f'Basic {auth_header}'
#         }
#
#         try:
#             response = requests.post(f'{settings.PAYME_URL}/create', json=payload, headers=headers)
#             response.raise_for_status()  # Raises an HTTPError for bad responses
#
#             result = response.json()
#             print("Payme API Response:", result)  # Log the response for debugging
#
#             if result.get('status') == 'success':
#                 return result.get('pay_link')
#             else:
#                 error_message = result.get('message', 'Failed to generate payment link')
#                 raise Exception(f"Payme API Error: {error_message}")
#         except requests.exceptions.RequestException as e:
#             raise Exception(f'Error communicating with Payme: {e}')
#         except json.JSONDecodeError as e:
#             raise Exception(f'Invalid JSON response from Payme: {e}')


# def generate_pay_link_view(request):
#     if request.method == 'POST':
#         # Get the raw order_id and amount from POST data
#         order_id_raw = request.POST.get('order_id')
#         amount = request.POST.get('amount')
#
#         # Ensure that order_id is numeric
#         order_id = re.sub(r'\D', '', order_id_raw)  # Remove all non-numeric characters
#
#         if not order_id.isdigit():
#             return JsonResponse({'error': 'Invalid order ID provided.'}, status=400)
#
#         # Convert order_id to integer
#         order_id = int(order_id)
#
#         # Ensure order exists
#         order = get_object_or_404(Order, id=order_id)
#
#         # Generate payment link
#         pay_link_generator = GeneratePayLink(order_id=order.id, amount=amount)
#         try:
#             pay_link = pay_link_generator.generate_link()
#             return JsonResponse({'pay_link': pay_link})
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#
#     return JsonResponse({'error': 'Invalid request method'}, status=400)


# class GeneratePayLinkSerializer(serializers.Serializer):
#     order_id = serializers.IntegerField()
#     amount = serializers.DecimalField(max_digits=10, decimal_places=2)


# class GeneratePayLinkAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#
#         # Validate the incoming data
#         serializer = GeneratePayLinkSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         order_id = serializer.validated_data['order_id']
#         amount = serializer.validated_data['amount']
#
#         # Create the payload for Payme API
#         payload = {
#             'm': settings.PAYME_MERCHANT_ID,
#             'ac.order_id': order_id,
#             'a': str(amount),  # Convert to string if necessary
#             'c': 'http://127.0.0.1:8000/payment-return/',
#             'callback_url': 'https://36d0-82-215-100-34.ngrok-free.app/payment-callback/',
#         }
#         try:
#             # Make a request to the Payme API
#             response = requests.post(f'{settings.PAYME_URL}/create', json=payload)
#             response.raise_for_status()  # Raises an error for HTTP 4XX/5XX responses
#
#             result = response.json()
#             if result.get('status') == 'success':
#                 return Response({"pay_link": result.get('pay_link')}, status=status.HTTP_200_OK)
#             else:
#                 return Response({"error": result.get('message', 'Failed to generate payment link')},
#                                 status=status.HTTP_400_BAD_REQUEST)
#         except requests.exceptions.RequestException as e:
#             return Response({"error": f"Error communicating with Payme: {str(e)}"},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @csrf_exempt
# def payme_payment(request):
#     if request.method == "POST":
#         order_id = request.POST.get('order_id')
#         amount = request.POST.get('amount')
#
#         # Payme.uz tomonidan talab qilingan sha256 hashingni yaratish
#         merchant_key = settings.PAYME_MERCHANT_KEY
#         token = hashlib.sha256((order_id + amount + merchant_key).encode('utf-8')).hexdigest()
#
#         # To'lov ma'lumotlari
#         data = {
#             "amount": amount,
#             "order_id": order_id,
#             "merchant_id": settings.PAYME_MERCHANT_ID,
#             "token": token,
#         }
#
#         # To'lov so'rovini amalga oshiring
#         return JsonResponse(data)
#     return JsonResponse({'error': 'Only POST method is allowed'})


# class GeneratePayLinkAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         order_id = request.data.get('order_id')
#         amount = request.data.get('amount')
#         # Buyurtmani bazadan olish
#         # order = get_object_or_404(Order, order_id=order_id)
#         order = Order.objects.get(id=order_id)
#
#         # Payme.uz API so'rovini yuborish
#         headers = {'Content-Type': 'application/json'}
#         data = {
#             "method": "cards.create",
#             "params": {
#                 "amount": int(float(amount) * 100),  # tiyin ko'rinishida
#                 "account": {"order_id": order_id}
#             }
#         }
#         response = requests.post(PAYME_API_URL, json=data, headers=headers)
#         payme_response = response.json()
#
#         # Muvaffaqiyatli javobni tekshirish
#         if "result" in payme_response:
#             pay_link = payme_response["result"]["pay_link"]
#             return JsonResponse({"pay_link": pay_link})
#         else:
#             return JsonResponse({"error": payme_response.get("error", "Payment failed")}, status=400)


# def payment_view(request, order_id):
#     try:
#         # Ensure you use the numeric ID, not the string representation of the Order object
#         order = Order.objects.get(id=order_id)  # order_id should be an integer
#         amount = order.amount
#
#         # Generate the payment link
#         pay_link = GeneratePayLink(order_id=order.order_id, amount=amount).generate_link()  # Use order.id here
#
#         return render(request, 'payments.html', {
#             'order': order,
#             'amount': amount,
#             'pay_link': pay_link
#         })
#
#     except Order.DoesNotExist:
#         return render(request, 'error.html', {'message': 'Order not found'})


# def payment_view(request):
#
#     # order_id ni POST so'rovdan olish
#     order_id = request.GET.get('order_id')
#
#     if not order_id:  # Agar order_id bo'sh bo'lsa
#         return render(request, 'error.html', {'message': 'Order ID mavjud emas yoki noto\'g\'ri'})
#
#     # Ma'lumotlar bazasidan orderni olish
#     order = get_object_or_404(Order, id=order_id)
#     amount = order.amount
#
#     # To'lov linkini yaratish
#     pay_link = GeneratePayLink(order_id=order_id, amount=amount).generate_link()
#
#     return render(request, 'payments.html', {
#         'order_id': order,
#         'amount': amount,
#         'pay_link': pay_link
#     })


#
# @csrf_exempt
# def payment_callback(request):
#     if request.method == 'POST':
#         # Payme.uz'dan kelgan ma'lumotlarni olish
#         data = request.POST
#         order_id = data.get('order_id')
#         status = data.get('status')
#
#         # Buyurtmani yangilash
#         try:
#             order = Order.objects.get(order_id=order_id)
#             if status == 'completed':
#                 order.status = 'completed'
#                 order.save()
#                 return HttpResponse('To\'lov muvaffaqiyatli amalga oshirildi!')
#             else:
#                 return HttpResponse('To\'lov amalga oshirilmadi.')
#         except Order.DoesNotExist:
#             return HttpResponse('Buyurtma topilmadi.')
#     else:
#         return HttpResponse('No POST data received.')


class PaymeCallBackAPIView(MerchantAPIView):
    def create_transaction(self, order_id, action, *args, **kwargs) -> None:
        print(f"create_transaction for order_id: {order_id}, response: {action}")

    def perform_transaction(self, order_id, action, *args, **kwargs) -> None:
        print(f"perform_transaction for order_id: {order_id}, response: {action}")

    def cancel_transaction(self, order_id, action, *args, **kwargs) -> None:
        print(f"cancel_transaction for order_id: {order_id}, response: {action}")


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
                'callback_url': 'https://b4fa-82-215-100-34.ngrok-free.app/payments/merchant/',
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
