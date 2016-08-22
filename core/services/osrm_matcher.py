'''
    Basic utilities for matching coordinates to the street grid
    using the OSRM match endpoint
'''
import logging
import requests
from django.conf import settings
from cta_dump_viewer.models import OsmWayNode

logger = logging.getLogger(__name__)


def match_response(coord_string, radius_string):
    options = {
        'radiuses': radius_string,
        'geometries': 'geojson',
        'annotations': 'true',
        'overview': 'full',
    }
    request_url = '{}/{}'.format(settings.OSRM.MATCH_ENDPOINT, coord_string)
    logger.debug('Request url: {}'.format(request_url))
    response = requests.get(request_url, params=options)
    return response.json()


def match(coords, radiuses):
    coord_string = ';'.join(
        "%s,%s" % (lon, lat) for lon, lat in coords
    )
    output = match_response(coord_string, ';'.join(map(str, radiuses)))
    logger.debug('Match response: {}'.format(output))
    if 'tracepoints' not in output:
        logger.error('No tracepoints found for {}'.format(output))
        raise IOError(output)
    unsnapped_points = []
    for index, tracepoint in enumerate(output['tracepoints']):
        if not tracepoint:
            logger.warning('Tracepoint index {} not found'.format(index))
            unsnapped_points.append(index)
    return output, unsnapped_points


def naive_match(coords):
    radiuses = [settings.OSRM.DEFAULT_RADIUS] * len(coords)
    output, unsnapped_points = match(coords, radiuses)
    snapped_points = [
        tracepoint['location']
        for tracepoint
        in output['tracepoints']
        if tracepoint
    ]
    nodes = []
    for tracepoint in output['tracepoints']:
        if tracepoint:
            route = output['matchings'][tracepoint['matchings_index']]
            legs = route['legs']
            if tracepoint['waypoint_index'] == len(legs):
                continue
            leg = legs[tracepoint['waypoint_index']]
            leg_nodes = leg['annotation']['nodes']
            for node in leg_nodes:
                if node not in nodes:
                    nodes.append(node)

            way_nodes_lookup = {}
            for i in range(len(nodes)-1):
                begin_node = nodes[i]
                end_node = nodes[i+1]
                way_nodes = OsmWayNode.objects.raw("""
                    select
                        n.id osm_node_id,
                        osm_way_id,
                        st_x(st_transform(
                            st_geomfromtext('point('||n.lon/100||' '||n.lat/100||')', 3785),
                            4326
                        )) longitude,
                        st_y(st_transform(
                            st_geomfromtext('point('||n.lon/100||' '||n.lat/100||')', 3785),
                            4326
                        )) latitude
                    from
                    (
                        select id osm_way_id, unnest(nodes) node_id from planet_osm_ways where id =
                        (
                            select id
                            from planet_osm_ways
                            where nodes @> ARRAY[{}::bigint]
                            and nodes @> ARRAY[{}::bigint]
                            order by array_length(nodes, 1)
                            limit 1
                        )
                    ) nodes
                    join planet_osm_nodes n on (node_id = n.id)
                """.format(begin_node, end_node))
                if len(list(way_nodes)) > 0:
                    way_id = way_nodes[0].osm_way_id
                    if way_id not in way_nodes_lookup:
                        way_nodes_lookup[way_id] = way_nodes

    return snapped_points, way_nodes_lookup
