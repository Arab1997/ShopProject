from django.db import models
from accounts.models import Account
from store.models import Product, Variation
from django.utils.translation import gettext_lazy as _
class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default='New')
    created_at = models.DateTimeField(auto_now_add=True)

    # To'lov va buyurtma o'rtasidagi bog'lanish
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    transaction_id = models.CharField(max_length=255, unique=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.payment_id

    class Meta:
        verbose_name = _('Оплата')
        verbose_name_plural = _('Оплаты')

class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True, related_name='order_payments')
    order_id = models.CharField(max_length=20, unique=True,blank=True)  # Order ID-ni avtomatik generatsiya qilish uchun blank=True
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS, default='New')
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
    tax = models.IntegerField()
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Ensure this returns a simple string representation, not combined with other strings
        return f'Order {self.id}'

    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    #
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'


    class Meta:
        verbose_name = _('Заказ')
        verbose_name_plural = _('Заказы')
    # def __str__(self):
    #     return f'Order {self.order_id} - {self.status}'


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

    class Meta:
        verbose_name = _('Заказать продукт')
        verbose_name_plural = _('Заказать продукты')