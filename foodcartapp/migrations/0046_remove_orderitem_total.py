# Generated by Django 5.2.1 on 2025-05-11 11:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_orderitem_total'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='total',
        ),
    ]
