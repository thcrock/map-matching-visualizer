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


def build_raw_feature(way_id, raw_points, raw_indices):
    return geojson.Feature(
        geometry=geojson.MultiPoint([raw_points[i] for i in raw_indices]),
        properties={
            'way_id': way_id
        }
    )


def index(request):
    raw_points = points(48661914)
    match_output = osrm_matcher.match_response(raw_points)
    snapped = geojson.GeometryCollection([
        geojson.Point(coord)
        for coord in osrm_matcher.snapped_points(match_output)
    ])
    nodes = osrm_matcher.extract_nodes(match_output)
    node_pairs = osrm_matcher.generate_node_pairs(nodes)

    ways = osm_querier.lookup_ways(node_pairs)
    way_lookup = dict((o.id, o) for o in ways)
    ways_nodes = osm_querier.lookup_way_nodes(ways)

    raw_features = geojson.FeatureCollection([
        build_raw_feature(way_id, raw_points, way.raw_indices)
        for way_id, way in way_lookup.iteritems()
    ])
    way_features = geojson.FeatureCollection([
        build_way_feature(way_id, data, way_lookup[way_id])
        for way_id, data in ways_nodes.iteritems()
    ])
    return render(
        request,
        'cta_dump_viewer/index.html',
        Context({
            'raw_geojson': mark_safe(raw_features),
            'rawline_geojson': mark_safe(geojson.LineString(raw_points)),
            'snapped_geojson': mark_safe(snapped),
            'ways_geojson': mark_safe(way_features)
        })
    )
