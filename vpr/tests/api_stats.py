from django.db import connection

SQL_COUNT = 'select count(id) from vpr_api_apirecord where %s=%s;'

def countValue(field, value, time_start=None, time_end=None):
    cur = connection.cursor()
    cur.execute(SQL_COUNT % (field, value))
    return cur.fetchone()


