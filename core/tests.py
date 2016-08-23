from unittest import TestCase
import json
import os
import responses
import urlparse
from django.conf import settings
import core.services.osrm_matcher as matcher


class OsrmMatcherTestCase(TestCase):
    def test_match_response(self):
        coords = [(1, 2), (3, 4)]
        radiuses = [5, 6]
        with responses.RequestsMock() as rsps:
            response = '{"tracepoints": "not found"}'
            rsps.add(
                responses.GET,
                os.path.join(settings.OSRM.MATCH_ENDPOINT, '1,2;3,4'),
                body=response,
                status=200,
                content_type='application/json'
            )
            self.assertEqual(
                matcher.match_response(coords, radiuses),
                json.loads(response)
            )

            self.assertEqual(len(rsps.calls), 1)

            parsed_params = urlparse.parse_qs(
                urlparse.urlparse(rsps.calls[0].request.url).query
            )
            self.assertEqual(parsed_params['radiuses'], ['5;6'])
            self.assertEqual(parsed_params['annotations'], ['true'])

    def test_match_response_notracepoints(self):
        coords = [(1, 2), (3, 4)]
        radiuses = [5, 6]
        with responses.RequestsMock() as rsps:
            response = '{"something": "not found"}'
            rsps.add(
                responses.GET,
                os.path.join(settings.OSRM.MATCH_ENDPOINT, '1,2;3,4'),
                body=response,
                status=200,
                content_type='application/json'
            )
            with self.assertRaises(IOError):
                matcher.match_response(coords, radiuses)

    def test_unsnapped_points_all_snapped(self):
        output = {'tracepoints': [1, 2]}
        unsnapped = matcher.unsnapped_points(output)
        self.assertEqual(unsnapped, [])

    def test_unsnapped_points_some_snapped(self):
        output = {'tracepoints': [1, None]}
        unsnapped = matcher.unsnapped_points(output)
        self.assertEqual(unsnapped, [1])

    def test_snapped_points(self):
        output = {'tracepoints': [
            {'location': (1, 2)},
            None,
            {'location': (3, 4)}
        ]}
        snapped = matcher.snapped_points(output)
        self.assertEqual(snapped, [(1, 2), (3, 4)])
