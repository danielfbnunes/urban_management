from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, primary_key=True)


class Status(models.TextChoices):
    TO_VALIDATE = 'to_validate', _('to_validate')
    VALIDATED = 'validated', _('validated')
    SOLVED = 'solved', _('solved')


class Category(models.TextChoices):
    CONSTRUCTION = 'construction', _('construction')
    SPECIAL_EVENT = 'special_event', _('special_event')
    INCIDENT = 'incident', _('incident')
    WEATHER_CONDITION = 'weather_condition', _('weather_condition')
    ROAD_CONDITION = 'road_condition', _('road_condition')


class Occurrence(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    point = gis_models.PointField(geography=True)
    description = models.CharField(max_length=255)
    creation_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.TO_VALIDATE)
    category = models.CharField(max_length=30, choices=Category.choices)
