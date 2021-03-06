import itertools as itt
from math import sqrt
import networkx as nx
from core.preprocessors.base import PreprocessorBase


class MSTProcessor(PreprocessorBase):
    def mst(self, points_list, combinations, lat_index, lon_index):
        G = nx.Graph()
        for f, t in combinations:
            p1 = points_list[f]
            p2 = points_list[t]
            p2x = float(p2[lon_index])
            p1x = float(p1[lon_index])
            p2y = float(p2[lat_index])
            p1y = float(p1[lat_index])
            dX = p2x-p1x
            dY = p2y-p1y
            lenV = sqrt(dX*dX+dY*dY)
            G.add_edge(f, t, weight=lenV)
        return nx.minimum_spanning_tree(G)

    def ordered_path(self, mst, combinations):
        length0 = nx.all_pairs_dijkstra_path_length(mst)
        lMax = 0
        for f, t in combinations:
            lCur = length0[f][t]
            if lCur > lMax:
                lMax = lCur
                best = (f, t)
        return nx.dijkstra_path(mst, best[0], best[1])

    def preprocess(self):
        combinations = list(itt.combinations(range(len(self.coords)), 2))
        indices = self.ordered_path(
            self.mst(self.coords, combinations, 1, 0),
            combinations
        )
        return [self.coords[idx] for idx in indices]
