from __future__ import unicode_literals


class OsmWay(object):
    def __init__(self, pk, raw_indices, nodes, tags):
        self.id = pk
        self.raw_indices = raw_indices
        self.nodes = nodes
        self.tags = tags
