SCHEMAS = dict()

def register_schema(key, cls):
    SCHEMAS[key] = cls

def get_schema(key):
    return SCHEMAS[key]
