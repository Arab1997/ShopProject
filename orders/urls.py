from django.urls import path

from . import views
from .models import PaymeCheckoutView
from .views import payment_confirmation,  PaymentConfirmationView
urlpatterns = [
    # path('payme/endpoint/', TestView.as_view()),
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),

    path('payme-checkout/', PaymeCheckoutView.as_view(), name='payme_payment'),
    path('payment-confirmation/<int:payment_id>/', PaymentConfirmationView.as_view(), name='payment_confirmation'),

    path('payme/checkout/', PaymeCheckoutView.as_view(), name='payme_checkout'),
    path('payme/confirmation/<int:payment_id>/', payment_confirmation, name='payment_confirmation'),
]




