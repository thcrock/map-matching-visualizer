from django.shortcuts import render
from django.template import Context
from django.utils.safestring import mark_safe
import geojson
from cta_dump_viewer.models import Reading
from core.services.osrm_matcher import naive_match


def points(serial_number):
    return [
        (float(reading.longitude), float(reading.latitude)) for reading in
        Reading.objects.filter(serial_number=serial_number).all()
    ]


def index(request):
    raw_points = points(48661914)
    raw = geojson.LineString(raw_points)
    matched_points, way_nodes_lookup = naive_match(raw_points)
    ways = geojson.GeometryCollection([
        geojson.LineString([(node.longitude, node.latitude) for node in way_nodes])
        for way_nodes in way_nodes_lookup.values()
    ])
    snapped = geojson.GeometryCollection(
        [geojson.Point(coord) for coord in matched_points]
    )
    return render(
        request,
        'cta_dump_viewer/index.html',
        Context({
            'raw_geojson': mark_safe(raw),
            'snapped_geojson': mark_safe(snapped),
            'ways_geojson': mark_safe(ways)
        })
    )
