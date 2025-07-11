# Generated by Django 5.2.1 on 2025-05-15 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100, unique=True, verbose_name='адрес')),
                ('latitude', models.FloatField(null=True, verbose_name='широта')),
                ('longitude', models.FloatField(null=True, verbose_name='долгота')),
                ('geocode_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата последнего запроса к geocoder')),
            ],
            options={
                'verbose_name': 'локация',
                'verbose_name_plural': 'локации',
            },
        ),
    ]
