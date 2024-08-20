from django.urls import path

from . import views
from .views import PaymeCheckoutView, payment_confirmation, TestView

urlpatterns = [
    path('payme/endpoint/', TestView.as_view()),

    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),

    path('payme/checkout/', PaymeCheckoutView.as_view(), name='payme_checkout'),
    path('payme/confirmation/<int:payment_id>/', payment_confirmation, name='payment_confirmation'),
]




