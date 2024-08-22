from django.db import models
from django.shortcuts import redirect
from django.views import View
from accounts.models import Account
from store.models import Product, Variation
from paycomuz import Paycom
from django.urls import reverse


class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    # Add the default value here
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transaction_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.payment_id

class CheckOrder(Paycom):
    def check_order(self, amount, account, *args, **kwargs):
        return self.ORDER_FOUND

class PaymeCheckoutView(View):
    def post(self, request):
        amount = request.POST.get('amount')
        order_id = request.POST.get('order_id')

        # Create a payment instance
        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
            transaction_id=order_id,
            status='Pending'
        )
        # Redirect to a confirmation page or handle payment process
        return redirect(reverse('payment_confirmation', args=[payment.id]))
        print(f"Amount: {amount}, Order ID: {order_id}")

class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    _id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=255)


# class Payment(models.Model):
#     user = models.ForeignKey(Account, on_delete=models.CASCADE)
#     payment_id = models.CharField(max_length=100)
#     payment_method = models.CharField(max_length=100)
#     status = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     transaction_id = models.CharField(max_length=100, unique=True)
#
#     def __str__(self):
#         return self.payment_id

class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name
