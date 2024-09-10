from django.urls import path

from . import views
from .views import PaymeCallBackAPIView,  SendCheckView

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('order_complete/', views.order_complete, name='order_complete'),

    # path('generate-pay-link/', GeneratePayLinkAPIView.as_view(), name='generate_pay_link'),
    path('payme-callback/', PaymeCallBackAPIView.as_view(), name='payme_callback'),

    # to'g'ri yo'naltirish
    # path('payme/payme_payment/', views.payme_payment, name='payme_payment'),  # to'g'ri yo'naltirish

    # path('payme/payment/', views.payment_view, name='payment_view'),  # to'g'ri yo'naltirish
    # path('payment/callback/', views.payment_callback, name='payment_callback'),

    # path('orders/payme/payment/<int:order_id>/', views.payment_view, name='payment_view'),

    # path('pay-link/', GeneratePayLinkAPIView.as_view(), name='generate_pay_link'),

    # path('generate-pay-link/', generate_pay_link_view, name='generate_pay_link'),
    # path('pay-link/', GeneratePayLinkAPIView.as_view(), name='generate-pay-link'),


    # path('payme/send-check/', SendCheckView.as_view(), name='send_check'),

    path('send-check/', SendCheckView.as_view(), name='send_check'),

]
