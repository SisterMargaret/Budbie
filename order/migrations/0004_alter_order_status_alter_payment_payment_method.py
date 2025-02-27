# Generated by Django 4.1.2 on 2023-04-24 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_alter_order_tax_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Accepted', 'Accepted'), ('Ready', 'Ready'), ('Rejected', 'Rejected'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='New', max_length=15),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(choices=[('PayPal', 'PayPal'), ('RazorPay', 'RazorPay'), ('ApplePay', 'ApplePay'), ('GooglePay', 'GooglePay'), ('Stripe', 'Stripe')], max_length=100),
        ),
    ]
