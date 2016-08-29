import abc


class BaseMatcher(object):
    __metaclass__ = abc.ABCMeta
    _output = None
    _nodes = None

    def __init__(self, raw_coords, radiuses=None):
        self.raw_coords = raw_coords
        self.radiuses = radiuses

    @property
    def nodes(self):
        self._nodes = self._nodes or self._generate_nodes()
        return self._nodes

    @property
    def output(self):
        self._output = self._output or self._match_output()
        return self._output

    def snapped_points(self):
        pass

    def generate_node_pairs(self):
        return [
            (self.nodes[i], self.nodes[i+1])
            for i in range(len(self.nodes)-1)
        ]

    @abc.abstractmethod
    def _match_output(self):
        pass

    @abc.abstractmethod
    def _generate_nodes(self):
        pass
