from unittest import TestCase
import json
import os
import responses
import urlparse
from django.conf import settings
from core.services.osrm_matcher import match_response


class OsrmMatcherTestCase(TestCase):
    def test_match_response(self):
        coords = 'coords'
        radius = 'radiuses'
        with responses.RequestsMock() as rsps:
            response = '{"error": "not found"}'
            rsps.add(
                responses.GET,
                os.path.join(settings.OSRM.MATCH_ENDPOINT, coords),
                body=response,
                status=200,
                content_type='application/json'
            )
            self.assertEqual(
                match_response(coords, radius),
                json.loads(response)
            )

            self.assertEqual(len(rsps.calls), 1)

            parsed_params = urlparse.parse_qs(
                urlparse.urlparse(rsps.calls[0].request.url).query
            )
            self.assertEqual(parsed_params['radiuses'], ['radiuses'])
            self.assertEqual(parsed_params['annotations'], ['true'])
