import logging
import os

from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers import parse, is_valid_number, NumberParseException, format_number, PhoneNumberFormat
from rest_framework.serializers import ModelSerializer, ListField, ValidationError, \
    CharField

from .models import OrderItem, Product, Order
from restaurateur.utils import get_or_update_address
logger = logging.getLogger(__name__)


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
    products = OrderItemSerializer(many=True, write_only=True, min_length=1)
    phonenumber = PhoneNumberField()

    class Meta:
        model = Order
        fields = ['products', 'firstname',
                  'lastname', 'phonenumber', 'address']

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        phonenumber = validated_data.pop('phonenumber')
        address = validated_data.pop('address')

        api_key = os.getenv("YANDEX_GEOCODER_KEY")
        if not api_key:
            logger.error("Не найден API-ключ Яндекс.Геокодера")
        client_address = get_or_update_address(address, api_key)

        order = Order.objects.create(
            phonenumber=phonenumber,
            address=address,
            **validated_data
        )
        order_items = [
            OrderItem(
                order=order,
                product=product_data['product'],
                quantity=product_data['quantity'],
                fixed_price=product_data['product'].price
            )
            for product_data in products_data
        ]
        OrderItem.objects.bulk_create(order_items)

        return order
