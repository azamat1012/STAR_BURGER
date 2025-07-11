# Generated by Django 5.2.1 on 2025-05-09 12:34

from django.db import migrations
from phonenumber_field.phonenumber import PhoneNumber


def normalize_phone_numbers(app, schema_editor):
    Order = app.get_model('foodcartapp', 'Order')
    total_order = Order.objects.all()
    for order in total_order:
        try:
            if order.phonenumber:
                phone = PhoneNumber.from_string(
                    order.phonenumber, region='RU')
                order.phonenumber = phone.as_e164
                order.save()
        except ValueError:
            print(
                f"Некорректный номер телефона для заказа {order.id}: {order.phonenumber}")




class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_order_user_orderitem'),
    ]

    operations = [
        migrations.RunPython(normalize_phone_numbers)
    ]



