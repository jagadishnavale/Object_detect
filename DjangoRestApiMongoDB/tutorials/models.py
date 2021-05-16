from django.db import models
from django.db.models.aggregates import Max


class Tutorial(models.Model):
    title = models.CharField(max_length=70, blank=False, default='')
    description = models.CharField(max_length=200, blank=False, default='')
    published = models.BooleanField(default=False)


class FileDetails(models.Model):
    fileName = models.CharField(max_length=200, blank=False, default='')
    coordinates = models.CharField(max_length=10000, blank=False, default='')
    timestamp = models.DateTimeField(auto_now_add=True)
