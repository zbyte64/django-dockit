SCHEMAS = dict()

def register_schema(key, cls):
    SCHEMAS[key] = cls

def get_schema(key):
    return SCHEMAS[key]

class DotPathTraverser(object):
    def __init__(self, dotpath):
        self.dotpath = dotpath
        self.remaining_paths = dotpath.split('.')
        self.resolved_paths = list() #part, value, field
    
    def resolve_next(self):
        current = self.resolved_paths[-1]
        current['value']
        current['field']
    
    @property
    def next_part(self):
        return self.remaining_parts[0]
