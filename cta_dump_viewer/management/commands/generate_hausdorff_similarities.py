from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Matches bus run and trip schedule geometries by hausdorff distance'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute('drop table if exists cta_dump_viewer_route_similarities')
            cursor.execute('''
                create table cta_dump_viewer_route_similarities as
                select
                    sl.shape_id,
                    serial_number,
                    r.departure_timestamp,
                    t.trip_id,
                    st_hausdorffdistance(sl.shapegeom, r.tripgeom),
                    stop_times.departure_time as scheduled_departure
                from cta_dump_viewer_runs r
                    join trips t on (route_id = route and replace(replace(direction, 'South', '2'), 'North', '1')::int = direction_id)
                    join calendar c on (
                        t.service_id = c.service_id and
                        departure_timestamp >= start_date::timestamp and
                        departure_timestamp < (end_date + interval '1d')::timestamp and
                        (
                            (to_char(departure_timestamp, 'day') = rpad('monday', 9) and monday = 't') or 
                            (to_char(departure_timestamp, 'day') = rpad('tuesday', 9) and tuesday = 't') or 
                            (to_char(departure_timestamp, 'day') = rpad('wednesday', 9) and wednesday = 't') or 
                            (to_char(departure_timestamp, 'day') = rpad('thursday', 9) and thursday = 't') or 
                            (to_char(departure_timestamp, 'day') = rpad('friday', 9) and friday = 't') or 
                            (to_char(departure_timestamp, 'day') = rpad('saturday', 9) and saturday = 't') or 
                            (to_char(departure_timestamp, 'day') = rpad('sunday', 9) and sunday = 't')
                        )
                    )
                    join shapes_lines sl using (shape_id)
                    join stop_times on (stop_times.trip_id = t.trip_id and stop_sequence = 1)
                group by 1, 2, 3, 4, 5, 6
                order by 5 desc
            ''')

            cursor.execute('drop table if exists cta_dump_viewer_likeliest_trips')
            cursor.execute('''create table cta_dump_viewer_likeliest_trips as
                select distinct on(serial_number)
                    serial_number,
                    trip_id,
                    combined_distance
                from (
                    select
                        serial_number,
                        trip_id,
                        (abs(extract(epoch from departure_timestamp::time - scheduled_departure::time))/86400) + st_hausdorffdistance as combined_distance
                    from cta_dump_viewer_route_similarities
                ) distances
                order by serial_number, combined_distance asc
            ''')

