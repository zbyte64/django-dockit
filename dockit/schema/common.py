from exceptions import DotPathNotFound

COLLECTIONS = dict()

def register_collection(cls):
    COLLECTIONS[cls._meta.collection] = cls

def get_base_document(key):
    return COLLECTIONS[key]

class UnSet(object):
    def __nonzero__(self):
        return False

class DotPathTraverser(object):
    def __init__(self, dotpath):
        self.dotpath = dotpath
        self.remaining_paths = dotpath.split('.')
        self.resolved_paths = list() #part, value, field
        self._finished = False
        self._called = False
    
    def resolve_for_schema(self, schema):
        from fields import SchemaField
        entry = {'value':None,
                 'field':SchemaField(schema=schema),
                 'part':None,}
        self.resolved_paths = [entry]
        self._resolve_loop()
    
    def resolve_for_instance(self, instance):
        from fields import SchemaField
        entry = {'value':instance,
                 'field':SchemaField(schema=type(instance)),
                 'part':None,}
        self.resolved_paths = [entry]
        self._resolve_loop()
    
    def _resolve_loop(self):
        while not self._finished:
            self._called = False
            self.resolve_next()
            if not self._called:
                assert False, str(self.resolved_paths)
            #need a better control routine, want one last resolve if end wasn't called
    
    def resolve_next(self):
        current = self.current
        if current['field'] is None:
            if hasattr(current['value'], 'traverse_dot_path'):
                current['value'].traverse_dot_path(self)
                #note the result may or may not have a field
            elif self.remaining_paths:
                raise DotPathNotFound('Arrived at a dead end', traverser=self)
            else:
                #nothing left to resolve
                self._finished = True
                self._called = True
        else:
            current['field'].traverse_dot_path(self)
    
    @property
    def next_part(self):
        return self.remaining_paths[0]
    
    @property
    def current(self):
        return self.resolved_paths[-1]
    
    @property
    def current_value(self):
        return self.current['value']
    
    def end(self, field=None, value=None):
        last_entry = self.resolved_paths[-1]
        if field:
            last_entry['field'] = field
        if value:
            last_entry['value'] = value
        assert len(self.remaining_paths) == 0
        self._finished = True
        self._called = True
    
    def next(self, field=None, value=None):
        part = self.remaining_paths.pop(0)
        if value and field is None:
            from fields import SchemaField
            from schema import Schema
            if isinstance(value, Schema):
                field = SchemaField(schema=type(value))
        entry = {'field':field,
                 'value':value,
                 'part':part,}
        self.resolved_paths.append(entry)
        self._called = True
    
    def set_value(self, value):
        parent_entry = self.resolved_paths[-2]
        part = self.current['part']
        if parent_entry['field']:
            parent_entry['field'].set_value(parent_entry['value'], part, value)
        elif parent_entry['value'] is not None:
            parent_entry['value'].set_value(part, value)
        else:
            assert False

class DotPathList(list):
    def traverse_dot_path(self, traverser):
        if traverser.remaining_paths:
            new_value = None
            name = traverser.next_part
            try:
                new_value = self[int(name)]
            except ValueError:
                raise DotPathNotFound("Invalid index given, must be an integer")
            except IndexError:
                pass
            traverser.next(value=new_value)
        else:
            traverser.end(value=self)
    
    def set_value(self, attr, value):
        index = int(attr)
        if value is UnSet:
            self.pop(index)
        elif index == len(self):
            self.append(value)
        else:
            self[index] = value

class DotPathDict(dict):
    def traverse_dot_path(self, traverser):
        if traverser.remaining_paths:
            new_value = None
            name = traverser.next_part
            try:
                new_value = self[name]
            except KeyError:
                pass
            traverser.next(value=new_value)
        else:
            traverser.end(value=self)
    
    def set_value(self, attr, value):
        if value is UnSet:
            del self[attr]
        else:
            self[attr] = value

class DotPathSet(set):
    def traverse_dot_path(self, traverser):
        if traverser.remaining_paths:
            raise DotPathNotFound("Cannot traverse past a set")
        else:
            traverser.end(value=self)
    
    def set_value(self, attr, value):
        if value is UnSet:
            self.remove(attr)
        else:
            self.add(value)

