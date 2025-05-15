from django.db import models
from django.utils import timezone


class Place(models.Model):
    address = models.CharField(
        'адрес',
        max_length=100,
        unique=True
    )
    latitude = models.FloatField(
        'широта',
        null=True,
    )
    longitude = models.FloatField(
        'долгота',
        null=True,
    )
    geocode_date = models.DateTimeField(
        "Дата последнего запроса к geocoder", auto_now_add=True, db_index=True)

    class Meta:
        app_label = 'places'
        verbose_name = "локация"
        verbose_name_plural = "локации"

    def __str__(self):
        return f"{self.address}: ({self.latitude}, {self.longitude})"
