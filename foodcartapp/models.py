from django.db import models
from django.db.models import F, Sum, DecimalField
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField


class User(models.Model):
    name = models.CharField(max_length=200)


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def total_price(self):
        return self.annotate(
            total=Sum(
                F('items__quantity') * F('items__fixed_price'),
                output_field=DecimalField()
            )
        )


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Необработанный'),
        ('processing', 'В обработке'),
        ('preparing', 'Готовится'),
        ('delivering', 'Доставляется'),
        ('completed', 'Завершен'),

    ]
    PAYMENT_CHOICES = [
        ('cash', 'Наличностью'),
        ('card', 'Электронно'),
    ]
    status = models.CharField('Статус', max_length=20,
                              choices=STATUS_CHOICES, default='new')
    firstname = models.CharField(verbose_name="Имя", max_length=50)
    lastname = models.CharField(
        verbose_name="Фамилия", max_length=50)
    address = models.CharField(
        verbose_name="Адрес", max_length=100)
    phonenumber = PhoneNumberField(
        verbose_name="Мобильный номер", null=True, unique=True, db_index=True)
    comment = models.TextField("Комментарий", max_length=250, blank=True)
    registered_at = models.DateTimeField(
        "Дата создания", auto_now_add=True, db_index=True)
    called_at = models.DateTimeField(null=True, blank=True, db_index=True)
    delivered_at = models.DateTimeField(null=True, blank=True, db_index=True)
    payment = models.CharField(
        "Оплата", choices=PAYMENT_CHOICES, max_length=20, default="cash")

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"{self.firstname} {self.lastname} {self.address}"


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items', verbose_name="заказ"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="products", verbose_name="продукт"
    )

    quantity = models.PositiveIntegerField(
        verbose_name="количество", validators=[MinValueValidator(1)]
    )
    fixed_price = models.DecimalField(
        "Цена",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=False
    )

    def save(self, *args, **kwargs):
        if not self.fixed_price:
            self.fixed_price = self.product.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Элементы заказа"
        verbose_name_plural = "Элементы заказов"

    def __str__(self):
        return f"{self.quantity} - {self.product.name}"
