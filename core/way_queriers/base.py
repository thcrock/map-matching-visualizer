import abc


class BaseWayQuerier(object):
    __metaclass__ = abc.ABCMeta
    _ways = None
    _ways_nodes = None

    def __init__(self, node_pairs):
        self.node_pairs = node_pairs

    @property
    def ways(self):
        self._ways = self._ways or self._generate_ways()
        return self._ways

    @property
    def ways_nodes(self):
        self._ways_nodes = self._ways_nodes or self._generate_ways_nodes()
        return self._ways_nodes

    def way_lookup(self):
        return dict((o.id, o) for o in self.ways)

    @abc.abstractmethod
    def _generate_ways(self):
        pass

    @abc.abstractmethod
    def _generate_ways_nodes(self):
        pass
