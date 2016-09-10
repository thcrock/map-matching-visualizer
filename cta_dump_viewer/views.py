from django.shortcuts import render
from django.template import Context
from django.utils.safestring import mark_safe
import geojson
from cta_dump_viewer.models import Reading
import core.matchers.osrm
import core.matchers.sample_osrm
import core.way_queriers.all
import core.way_queriers.fewest_nodes
import core.way_queriers.sample


AVAILABLE_MATCHERS = {
    'osrm': core.matchers.osrm.OsrmMatcher,
    'sample': core.matchers.sample_osrm.SampleOsrmMatcher
}

AVAILABLE_WAY_QUERIERS = {
    'all': core.way_queriers.all.AllWayQuerier,
    'fewest_nodes': core.way_queriers.fewest_nodes.FewestNodesWayQuerier,
    'sample': core.way_queriers.sample.SampleWayQuerier
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
            'tags': lookup_data.tags,
            'raw_indices': lookup_data.raw_indices
        }
    )


def build_raw_feature(raw_point, index):
    return geojson.Feature(
        geometry=geojson.Point(raw_point),
        properties={
            'raw_indices': [index]
        }
    )


def build_snapped_feature(snapped_point, index):
    return geojson.Feature(
        geometry=geojson.Point(snapped_point),
        properties={
            'raw_indices': [index]
        }
    )


def build_coupling_lines(raw_points, snapped_points):
    return geojson.GeometryCollection([
        geojson.LineString([raw_point, snapped_point])
        for raw_point, snapped_point in zip(raw_points, snapped_points)
        if snapped_point
    ])


def index(request):
    raw_points = points(48661914)
    matcher = AVAILABLE_MATCHERS['osrm'](raw_points)
    snapped_points = matcher.snapped_points()
    node_pairs = matcher.generate_node_pairs()

    way_querier = AVAILABLE_WAY_QUERIERS['fewest_nodes'](node_pairs)
    way_lookup = way_querier.way_lookup()

    raw_features = geojson.FeatureCollection([
        build_raw_feature(raw_point, index)
        for index, raw_point in enumerate(raw_points)
    ])
    snapped_features = geojson.FeatureCollection([
        build_snapped_feature(snapped_point, index)
        for index, snapped_point in enumerate(snapped_points)
        if snapped_point
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
            'coupling_geojson': mark_safe(build_coupling_lines(raw_points, snapped_points)),
            'ways_geojson': mark_safe(way_features)
        })
    )
