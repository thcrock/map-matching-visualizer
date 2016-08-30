from collections import defaultdict
from core.models import OsmWay
from django.db import connection
from core.way_queriers.base import BaseWayQuerier


class FewestNodesWayQuerier(BaseWayQuerier):
    def _generate_ways(self):
        node_pairs_query = ' union all '.join(
            'select {} n1, {} n2, {} rp1, {} rp2'
            .format(n1[0], n2[0], n1[1], n2[1])
            for n1, n2 in self.node_pairs
        )
        query = """
select distinct on (n1, n2) nodes, id, ARRAY[rp1, rp2], tags
from planet_osm_ways
join (
    {}
) node_pairs
on (
    nodes @> ARRAY[n1::bigint] and
    nodes @> ARRAY[n2::bigint]
)
order by n1, n2, array_length(nodes, 0) desc
        """.format(node_pairs_query)
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        print len(rows)
        return [OsmWay(row[1], row[2], row[3], row[0]) for row in rows]

    def _generate_ways_nodes(self):
        way_id_query = ' union all '.join(
            'select {} way_id'.format(way.id) for way in self.ways
        )
        query = """
    select
        way_id id,
        node_id,
        st_x(st_transform(
            st_geomfromtext('point('||n.lon/100||' '||n.lat/100||')', 3785),
            4326
        )) longitude,
        st_y(st_transform(
            st_geomfromtext('point('||n.lon/100||' '||n.lat/100||')', 3785),
            4326
        )) latitude
        from
        (
            select
                way_id,
                unnest(nodes) node_id
            from
            ({}) way_ids
            join planet_osm_ways on (id = way_id)
        ) nodes
        join planet_osm_nodes n on (node_id = n.id)
        """.format(way_id_query)
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        results = defaultdict(list)
        for way_id, node_id, lon, lat in rows:
            results[way_id].append({
                'coordinates': (lon, lat),
                'node_id': node_id
            })
        return results
