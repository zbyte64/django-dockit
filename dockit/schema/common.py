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
    
    def resolve_for_schema(self, schema):
        from fields import SchemaField
        entry = {'value':None,
                 'field':SchemaField(schema=schema),
                 'part':None,}
        self.resolved_paths = [entry]
    
    def resolve_for_instance(self, instance):
        from fields import SchemaField
        entry = {'value':instance,
                 'field':SchemaField(schema=type(instance)),
                 'part':None,}
        self.resolved_paths = [entry]
    
    def resolve_next(self):
        current = self.resolved_paths[-1]
        if current['field'] is None:
            pass
        else:
            current['field'].traverse_dot_path(self)
    
    @property
    def next_part(self):
        return self.remaining_parts[0]
    
    @property
    def current_value(self):
        return self.resolved_paths[-1]['value']
    
    def end(self, field=None, value=None):
        last_entry = self.resolved_paths[-1]
        if field:
            last_entry['field'] = field
        if value:
            last_entry['value'] = value
    
    def next(self, field=None, value=None):
        part = self.remaining_paths.pop(0)
        entry = {'field':field,
                 'value':value,
                 'part':part,}
        self.resolved_paths.append(entry)
