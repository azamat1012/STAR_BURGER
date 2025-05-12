from django.db import models
from django.utils import timezone


class Coordinate(models.Model):
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
        unique=True
    )
    latitude = models.FloatField(
        'широта',
        null=True,
        blank=True,
    )
    longitude = models.FloatField(
        'долгота',
        null=True,
        blank=True,
    )
    geocode_date = models.DateTimeField(
        "Дата последнего запроса к geocoder", default=timezone.now, db_index=True)

    class Meta:
        app_label = 'distances'
        verbose_name = "локация"
        verbose_name_plural = "локации"

    def __str__(self):
        return f"{self.address}: ({self.latitude}, {self.longitude})"
