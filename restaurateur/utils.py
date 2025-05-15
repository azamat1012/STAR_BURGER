import os
from datetime import datetime, timedelta
from django.utils import timezone
import logging
from dotenv import load_dotenv
from geopy import distance
import requests
from requests.exceptions import RequestException

from foodcartapp.models import RestaurantMenuItem, Restaurant
from places.models import Place

logger = logging.getLogger(__name__)


# def get_or_update_address(address, apikey):
#     """Получает или обновляет координаты для адреса"""
#     try:
#         coord, created = Place.objects.get_or_create(address=address)
#         if created:
#             logger.info(
#                 f"Создана новая запись координат для адреса: {address}")
#             coords = fetch_coordinates(apikey, address)
#             if coords:
#                 coord.latitude, coord.longitude = coords
#                 coord.geocode_date = timezone.now()
#                 coord.save()
#                 logger.info(
#                     f"Обновлены координаты для нового адреса: {address}")
#                 return coords
#             elif coord.latitude and coord.longitude:
#                 logger.debug(
#                     f"Используются существующие координаты для адреса: {address}")
#                 return (coord.latitude, coord.longitude)

#         return (coord.latitude, coord.longitude) if coord.latitude and coord.longitude else None
#     except Exception as e:
#         logger.error(
#             f"Ошибка при получении координат для адреса {address}: {str(e)}")
#         return None


def get_or_update_address(address, apikey):
    """Получает или обновляет координаты для адреса"""
    try:
        coord, created = Place.objects.get_or_create(address=address)
        if created:
            logger.info(
                f"Created new coordinates entry for address: {address}")
            coords = fetch_coordinates(apikey, address)
            if coords:
                coord.latitude, coord.longitude = coords
                coord.geocode_date = timezone.now()
                coord.save()
                logger.info(f"Updated coordinates for new address: {address}")
                logger.debug(
                    f"Fetched coordinates for address {address}: {coords}")
                return coords
            else:
                logger.warning(
                    f"Failed to fetch coordinates for address {address}")
        else:
            logger.debug(f"Using existing coordinates for address: {address}")

        return (coord.latitude, coord.longitude) if coord.latitude and coord.longitude else None
    except Exception as e:
        logger.error(
            f"Error fetching coordinates for address {address}: {str(e)}")
        return None


def get_available_restaurants(order):
    """Возвращает доступные рестораны с расстоянием до клиента"""
    load_dotenv()
    order_details = order.items.all()
    restaurants = Restaurant.objects.all()

    for detail in order_details:
        product = RestaurantMenuItem.objects.filter(
            product=detail.product,
            availability=True
        ).values_list('restaurant_id', flat=True)
        restaurants = restaurants.filter(id__in=product)
        if not restaurants.exists():
            logger.debug("Нет ресторанов с доступными товарами из заказа")
            return []

    api_key = os.getenv("YANDEX_GEOCODER_KEY")
    if not api_key:
        logger.error("Не найден API-ключ Яндекс.Геокодера")
        return

    client_coords = get_or_update_address(order.address, api_key)
    logger.debug(
        f"Адрес клиента: {order.address}, координаты: {client_coords}")
    if not client_coords:
        logger.warning(
            f"Не удалось получить координаты клиента: {order.address}")
        return

    restaurant_addresses = restaurants.values_list('address', flat=True)

    coord_map = {
        coord.address: (coord.latitude, coord.longitude)
        for coord in Place.objects.filter(
            address__in=restaurant_addresses, latitude__isnull=False, longitude__isnull=False
        )
    }

    available_restaurants = []
    for restaurant in restaurants:
        restaurant_coords = coord_map.get(restaurant.address)
        if not restaurant_coords:
            restaurant_coords = get_or_update_address(
                restaurant.address, api_key)

        distance_km = None
        if client_coords and restaurant_coords:
            try:
                distance_km = round(distance.distance(
                    client_coords, restaurant_coords).km, 3)
            except ValueError as e:
                logger.error(f"Error calculating distance: {str(e)}")
                continue

        available_restaurants.append({
            'restaurant': restaurant,
            'distance': distance_km,
        })

    return available_restaurants


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json(
    )['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat
