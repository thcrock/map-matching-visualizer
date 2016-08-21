# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-21 18:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Reading',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.IntegerField()),
                ('route', models.CharField(db_index=True, max_length=10)),
                ('direction', models.CharField(db_index=True, max_length=5)),
                ('vehicle_number', models.CharField(max_length=10)),
                ('date', models.DateField(db_index=True)),
                ('time', models.TimeField(db_index=True)),
                ('passengers_on', models.IntegerField()),
                ('passengers_off', models.IntegerField()),
                ('passengers_in', models.IntegerField()),
                ('latitude', models.CharField(max_length=10)),
                ('longitude', models.CharField(max_length=10)),
            ],
        ),
    ]