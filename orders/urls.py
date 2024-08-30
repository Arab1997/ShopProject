from django.urls import path

from . import views
from .views import PaymeCallBackAPIView, GeneratePayLinkAPIView

urlpatterns = [

    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),

    # payme pkg
    path('pay-link/', GeneratePayLinkAPIView.as_view(), name='generate-pay-link'),
    path('generate-pay-link/', GeneratePayLinkAPIView.as_view(), name='generate_pay_link'),
    path('payme-callback/', PaymeCallBackAPIView.as_view(), name='payme_callback'),

    path('payme/payment/', views.payme_payment, name='payme_payment'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),

    path('pay-link/', GeneratePayLinkAPIView.as_view(), name='generate_pay_link'),

]
