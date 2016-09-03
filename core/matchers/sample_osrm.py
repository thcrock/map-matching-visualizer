'''
    Basic utilities for matching coordinates to the street grid
    using the OSRM match endpoint
'''
from core.matchers.osrm import OsrmMatcher
import json
import os


class SampleOsrmMatcher(OsrmMatcher):
    def _match_output(self):
        sample_filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'sample_response.json'
        )
        with open(sample_filename, 'r') as f:
            return json.load(f)
