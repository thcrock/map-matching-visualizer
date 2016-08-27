from collections import defaultdict
from core.models import OsmWay
from django.db import connection


def lookup_ways(node_pairs):
    node_pairs_query = ' union all '.join(
        'select {} n1, {} n2, {} rp1, {} rp2'
        .format(n1[0], n2[0], n1[1], n2[1])
        for n1, n2 in node_pairs
    )
    query = """
        select id, n1, n2, ARRAY[rp1, rp2], tags, nodes
        from planet_osm_ways
        join (
            {}
        ) node_pairs
        on (
            nodes @> ARRAY[n1::bigint] and
            nodes @> ARRAY[n2::bigint]
        )
    """.format(node_pairs_query)
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return [OsmWay(row[0], row[3], row[4], row[5]) for row in rows]


def lookup_way_nodes(ways):
    way_id_query = ' union all '.join(
        'select {} way_id'.format(way.id) for way in ways
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
