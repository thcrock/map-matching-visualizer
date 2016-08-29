from django.shortcuts import render
from django.template import Context
from django.utils.safestring import mark_safe
import geojson
from cta_dump_viewer.models import Reading
import core.matchers.osrm
import core.way_queriers.all


AVAILABLE_MATCHERS = {
    'osrm': core.matchers.osrm.OsrmMatcher
}

AVAILABLE_WAY_QUERIERS = {
    'all': core.way_queriers.all.AllWayQuerier
}


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


def build_snapped_feature(way_id, snapped_points, indices):
    return geojson.Feature(
        geometry=geojson.MultiPoint([snapped_points[i] for i in indices]),
        properties={
            'way_id': way_id
        }
    )


def index(request):
    raw_points = points(48661914)
    matcher = AVAILABLE_MATCHERS['osrm'](raw_points)
    snapped_points = matcher.snapped_points()
    node_pairs = matcher.generate_node_pairs()

    way_querier = AVAILABLE_WAY_QUERIERS['all'](node_pairs)
    way_lookup = way_querier.way_lookup()

    raw_features = geojson.FeatureCollection([
        build_raw_feature(way_id, raw_points, way.raw_indices)
        for way_id, way in way_lookup.iteritems()
    ])
    snapped_features = geojson.FeatureCollection([
        build_snapped_feature(way_id, snapped_points, way.raw_indices)
        for way_id, way in way_lookup.iteritems()
    ])
    way_features = geojson.FeatureCollection([
        build_way_feature(way_id, data, way_lookup[way_id])
        for way_id, data in way_querier.ways_nodes.iteritems()
    ])
    return render(
        request,
        'cta_dump_viewer/index.html',
        Context({
            'raw_geojson': mark_safe(raw_features),
            'rawline_geojson': mark_safe(geojson.LineString(raw_points)),
            'snapped_geojson': mark_safe(snapped_features),
            'snappedline_geojson': mark_safe(geojson.LineString(snapped_points)),
            'ways_geojson': mark_safe(way_features)
        })
    )
