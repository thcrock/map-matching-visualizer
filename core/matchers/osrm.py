'''
    Basic utilities for matching coordinates to the street grid
    using the OSRM match endpoint
'''
import logging
import requests
from django.conf import settings
from core.matchers.base import BaseMatcher

logger = logging.getLogger(__name__)


class OsrmMatcher(BaseMatcher):
    def _match_output(self):
        coords = self.raw_coords
        coord_string = ';'.join(
            "%s,%s" % (lon, lat) for lon, lat in coords
        )
        radiuses = self.radiuses or [settings.OSRM.DEFAULT_RADIUS] * len(coords)
        radius_string = ';'.join(map(str, radiuses))
        options = {
            'radiuses': radius_string,
            'geometries': 'geojson',
            'annotations': 'true',
            'overview': 'full',
        }
        request_url = '{}/{}'.format(
            settings.OSRM.MATCH_ENDPOINT,
            coord_string
        )
        logger.debug('Request url: {}'.format(request_url))
        response = requests.get(request_url, params=options)
        output = response.json()
        if 'tracepoints' not in output:
            logger.error('No tracepoints found for {}'.format(output))
            raise IOError(output)
        logger.debug('Match response: {}'.format(output))
        return output

    def unsnapped_points(self):
        unsnapped_points = []
        for index, tracepoint in enumerate(self.output['tracepoints']):
            if not tracepoint:
                logger.warning('Tracepoint index {} not found'.format(index))
                unsnapped_points.append(index)
        return unsnapped_points

    def snapped_points(self):
        return [
            tracepoint.get('location') if tracepoint else None
            for tracepoint
            in self.output['tracepoints']
        ]

    def snapped_names(self):
        return [
            tracepoint.get('name') if tracepoint else None
            for tracepoint
            in self.output['tracepoints']
        ]

    def tracepoint_nodes(self, tracepoint_index):
        node_lookup = set()
        nodes = []
        tracepoint = self.output['tracepoints'][tracepoint_index]
        if tracepoint:
            legs = self.output['matchings'][tracepoint['matchings_index']]['legs']
            if len(legs) == tracepoint['waypoint_index']:
                return []
            leg = legs[tracepoint['waypoint_index']]
            for node in leg['annotation']['nodes']:
                if node not in node_lookup:
                    node_lookup.add(node)
                    nodes.append(node)
            return nodes
        else:
            return []

    def _generate_nodes(self):
        node_lookup = set()
        nodes = []
        for index, tracepoint in enumerate(self.output['tracepoints']):
            if tracepoint:
                route = self.output['matchings'][tracepoint['matchings_index']]
                legs = route['legs']
                if tracepoint['waypoint_index'] == len(legs):
                    continue
                leg = legs[tracepoint['waypoint_index']]
                leg_nodes = leg['annotation']['nodes']
                for node in leg_nodes:
                    if node not in node_lookup:
                        node_lookup.add(node)
                        nodes.append((node, index))
        return nodes
