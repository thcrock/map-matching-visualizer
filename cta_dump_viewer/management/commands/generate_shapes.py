from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Converts bus runs into line geometries'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute('drop table if exists cta_dump_viewer_runs')
            convert_runs_query = """
            create table cta_dump_viewer_runs as
            select
                serial_number,
                route,
                direction,
                min(date+time) as departure_timestamp,
                st_makeline(
                    st_makepoint(longitude::float, latitude::float)
                    order by date+time
                ) As tripgeom
                from cta_dump_viewer_reading
                group by serial_number, route, direction
            """
            cursor.execute(convert_runs_query)

            cursor.execute('drop table if exists shapes_lines')
            convert_shapes_query = """
            create table shapes_lines as
            select
                shape_id,
                st_makeline(geom order by shape_pt_sequence) as shapegeom
                from shapes
                group by shape_id
            """
            cursor.execute(convert_shapes_query)
