# Generated by Django 5.1 on 2024-09-05 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_amount_alter_order_order_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_id',
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
    ]
