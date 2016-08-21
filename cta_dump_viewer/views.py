from django.shortcuts import render
from django.template import Context
from django.utils.safestring import mark_safe
import geojson
from cta_dump_viewer.models import Reading


def index(request):
    raw = geojson.LineString([
        (float(reading.longitude), float(reading.latitude)) for reading in
        Reading.objects.filter(serial_number=48661914).all()
    ])
    return render(
        request,
        'cta_dump_viewer/index.html',
        Context({'raw_geojson': mark_safe(raw)})
    )
