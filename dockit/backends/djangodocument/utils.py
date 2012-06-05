from django.db import connection

def db_table_exists(table, cursor=None):
    if hasattr(connection.introspection, 'table_names'):
        return table in connection.introspection.table_names()
    else:
        if not cursor:
            cursor = connection.cursor()
        if not cursor:
            raise Exception
        table_names = connection.introspection.get_table_list(cursor)
        return table in table_names
