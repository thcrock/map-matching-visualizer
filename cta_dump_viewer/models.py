from __future__ import unicode_literals

from django.db import models


class Reading(models.Model):
    serial_number = models.IntegerField()
    route = models.CharField(max_length=10, db_index=True)
    direction = models.CharField(max_length=5, db_index=True)
    vehicle_number = models.CharField(max_length=10)
    date = models.DateField(db_index=True)
    time = models.TimeField(db_index=True)
    passengers_on = models.IntegerField()
    passengers_off = models.IntegerField()
    passengers_in = models.IntegerField()
    latitude = models.CharField(max_length=10)
    longitude = models.CharField(max_length=10)
