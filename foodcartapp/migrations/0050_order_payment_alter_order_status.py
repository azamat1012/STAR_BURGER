# Generated by Django 5.2.1 on 2025-05-11 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_alter_order_registered_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.CharField(choices=[('cash', 'Наличностью'), ('card', 'Электронно')], default='cash', max_length=20, verbose_name='Оплата'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('new', 'Необработанный'), ('processing', 'В обработке'), ('preparing', 'Готовится'), ('delivering', 'Доставляется'), ('completed', 'Завершен')], default='new', max_length=20, verbose_name='Статус'),
        ),
    ]
