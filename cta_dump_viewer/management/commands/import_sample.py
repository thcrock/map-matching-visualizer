from django.core.management.base import BaseCommand
from cta_dump_viewer.models import Reading
from django.conf import settings
import csv
import os


class Command(BaseCommand):
    help = 'Imports sample of cta data'

    def handle(self, *args, **options):
        filename = os.path.join(
            settings.CTA_DUMP.directory,
            settings.CTA_DUMP.sample_filename
        )
        objects = []
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            for line in reader:
                m, d, y = line[4].split('-')
                obj = Reading(
                    serial_number=line[0],
                    route=line[1],
                    direction=line[2],
                    vehicle_number=line[3],
                    date='-'.join([y, m, d]),
                    time=line[5] or '00:00:00',
                    passengers_on=line[6],
                    passengers_off=line[7],
                    passengers_in=line[8],
                    latitude=line[9],
                    longitude=line[10]
                )
                objects.append(obj)
        Reading.objects.bulk_create(objects)
