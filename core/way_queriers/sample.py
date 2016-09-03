import os
import pickle
from core.way_queriers.base import BaseWayQuerier


class SampleWayQuerier(BaseWayQuerier):
    def _generate_ways(self):
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'ways_sample.pickle'
        )
        with open(filename, 'r') as f:
            return pickle.load(f)

    def _generate_ways_nodes(self):
        filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'ways_nodes_sample.pickle'
        )
        with open(filename, 'r') as f:
            return pickle.load(f)
