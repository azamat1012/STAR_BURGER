from django.db import migrations, models
import django.core.validators


def forward(apps, schema_editor):
    OrderItem = apps.get_model('foodcartapp', 'OrderItem')
    for item in OrderItem.objects.all():
        if item.fixed_price is None or item.fixed_price == '':
            item.fixed_price = 0.00
            item.save()
        elif isinstance(item.fixed_price, str):
            try:
                item.fixed_price = float(item.fixed_price)
                item.save()
            except (ValueError, TypeError):
                item.fixed_price = 0.00
                item.save()


def backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('foodcartapp', '0054_alter_orderitem_options_alter_orderitem_fixed_price'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
        migrations.AlterField(
            model_name='orderitem',
            name='fixed_price',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=8,
                validators=[django.core.validators.MinValueValidator(0)],
                default=0.00,
                null=False,
                verbose_name='Цена'
            ),
        ),
    ]
