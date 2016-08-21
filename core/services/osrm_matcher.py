'''
    Basic utilities for matching coordinates to the street grid
    using the OSRM match endpoint
'''
import logging
import requests
from django.conf import settings

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
    print options
    response = requests.get(request_url, params=options)
    return response.json()


def match(lats, lons, radiuses):
    coord_string = ';'.join(
        "%s,%s" % (lon, lat) for lat, lon in zip(lats, lons)
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
