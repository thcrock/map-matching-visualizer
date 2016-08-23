from django.shortcuts import render
from django.template import Context
from django.utils.safestring import mark_safe
import geojson
from cta_dump_viewer.models import Reading
import core.services.osrm_matcher as osrm_matcher
import core.services.osm_querier as osm_querier


def points(serial_number):
    return [
        (float(reading.longitude), float(reading.latitude)) for reading in
        Reading.objects.filter(serial_number=serial_number).all()
    ]


def index(request):
    raw_points = points(48661914)
    raw = geojson.LineString(raw_points)
    match_output = osrm_matcher.match_response(raw_points)
    snapped = geojson.GeometryCollection([
        geojson.Point(coord)
        for coord in osrm_matcher.snapped_points(match_output)
    ])
    nodes = osrm_matcher.extract_nodes(match_output)
    node_pairs = osrm_matcher.generate_node_pairs(nodes)

    ways_nodes = osm_querier.lookup_way_nodes(
        osm_querier.lookup_ways(node_pairs)
    )
    ways = geojson.GeometryCollection([
        geojson.LineString(way_nodes)
        for way_nodes in ways_nodes
    ])
    return render(
        request,
        'cta_dump_viewer/index.html',
        Context({
            'raw_geojson': mark_safe(raw),
            'snapped_geojson': mark_safe(snapped),
            'ways_geojson': mark_safe(ways)
        })
    )
