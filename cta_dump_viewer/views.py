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


def build_way_feature(way_id, rows, lookup_data):
    return geojson.Feature(
        geometry=geojson.LineString([row['coordinates'] for row in rows]),
        properties={
            'node_ids': [row['node_id'] for row in rows],
            'way_id': way_id,
            'tags': lookup_data.tags
        }
    )


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

    ways = osm_querier.lookup_ways(node_pairs)
    way_lookup = dict((o.pk, o) for o in ways)
    ways_nodes = osm_querier.lookup_way_nodes(ways)
    way_features = geojson.FeatureCollection([
        build_way_feature(way_id, data, way_lookup[way_id])
        for way_id, data in ways_nodes.iteritems()
    ])
    return render(
        request,
        'cta_dump_viewer/index.html',
        Context({
            'raw_geojson': mark_safe(raw),
            'snapped_geojson': mark_safe(snapped),
            'ways_geojson': mark_safe(way_features)
        })
    )
