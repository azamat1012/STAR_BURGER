import json

from django.http import JsonResponse
from django.templatetags.static import static
from django.db import transaction

from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers import NumberParseException

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.serializers import ModelSerializer, ListField, ValidationError, \
    CharField
from .models import Product, Order, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['GET'])
def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return Response(dumped_products)


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'fixed_price']
        read_only = ['fixed_price']

    def validate_product(self, value):
        try:
            Product.objects.get(id=value.id)
            return value
        except Product.DoesNotExist:
            raise ValidationError(f"Недопустимый первичный ключ '{value.id}'")

    def validate_quantity(self, value):
        if not isinstance(value, int) or value < 1:
            raise ValidationError(
                "Количество должно быть целым числом больше 0")
        return value


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, write_only=True)
    phonenumber = CharField()

    class Meta:
        model = Order
        fields = ['products', 'firstname',
                  'lastname', 'phonenumber', 'address']

    def validate_string_fields(self, value, field_name):
        if not value:
            raise ValidationError(
                f"{field_name} - это поле не может быть пустым")
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} - not a valid string")
        return value

    def validate_firstname(self, value):
        return self.validate_string_fields(value, 'firstname')

    def validate_lastname(self, value):
        return self.validate_string_fields(value, 'lastname')

    def validate_address(self, value):
        return self.validate_string_fields(value, 'address')

    def validate_products(self, value):
        if not value:
            raise ValidationError("Этот список не может быть пустым")
        return value

    def validate_phonenumber(self, value):
        try:
            phone_number = PhoneNumber.from_string(value, region='RU')
            if not phone_number.is_valid():
                raise ValidationError("Введен некорректный номер телефона")
            return phone_number.as_e164
        except NumberParseException:
            raise ValidationError("Не валидный номер телефона")

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        phonenumber = validated_data.pop('phonenumber')
        order = Order.objects.create(
            phonenumber=phonenumber,
            **validated_data
        )
        for product_data in products_data:
            OrderItem.objects.create(
                order=order,
                product=product_data['product'],
                quantity=product_data['quantity'],
                fixed_price=product_data['product'].price
            )
        return order


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    with transaction.atomic():
        order = serializer.save()
        return Response(OrderSerializer(order).data)
