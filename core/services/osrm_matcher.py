'''
    Basic utilities for matching coordinates to the street grid
    using the OSRM match endpoint
'''
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def match_response(coords, radiuses=None):
    coord_string = ';'.join(
        "%s,%s" % (lon, lat) for lon, lat in coords
    )
    radiuses = radiuses or [settings.OSRM.DEFAULT_RADIUS] * len(coords)
    radius_string = ';'.join(map(str, radiuses))
    options = {
        'radiuses': radius_string,
        'geometries': 'geojson',
        'annotations': 'true',
        'overview': 'full',
    }
    request_url = '{}/{}'.format(settings.OSRM.MATCH_ENDPOINT, coord_string)
    logger.debug('Request url: {}'.format(request_url))
    response = requests.get(request_url, params=options)
    output = response.json()
    if 'tracepoints' not in output:
        logger.error('No tracepoints found for {}'.format(output))
        raise IOError(output)
    logger.debug('Match response: {}'.format(output))
    return output


def unsnapped_points(output):
    unsnapped_points = []
    for index, tracepoint in enumerate(output['tracepoints']):
        if not tracepoint:
            logger.warning('Tracepoint index {} not found'.format(index))
            unsnapped_points.append(index)
    return unsnapped_points


def snapped_points(output):
    return [
        tracepoint['location']
        for tracepoint
        in output['tracepoints']
        if tracepoint
    ]


def extract_nodes(output):
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
    return nodes


def generate_node_pairs(nodes):
    return [(nodes[i], nodes[i+1]) for i in range(len(nodes)-1)]
