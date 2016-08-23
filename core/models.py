from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import ArrayField


class OsmWay(models.Model):
    id = models.BigIntegerField(primary_key=True)
    nodes = ArrayField(models.BigIntegerField())
    tags = ArrayField(models.CharField(max_length=30))

    class Meta:
        db_table = 'planet_osm_ways'
        managed = False
