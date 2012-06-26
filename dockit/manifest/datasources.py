from common import DataSource, get_adaptor

from urllib2 import urlopen

class URLDataSource(DataSource):
    def __init__(self, url, **options):
        self.url = url
        super(URLDataSource, self).__init__(**options)
    
    def get_data(self):
        response = urlopen(self.url)
        adaptor = get_adaptor(self.options['format'])
        data = adaptor.deserialize(response)
        return data

class InlineDataSource(DataSource):
    def __init__(self, data, **options):
        self.data = data
        super(InlineDataSource, self).__init__(**options)
    
    def get_data(self):
        return self.data

class LocalDataSource(DataSource):
    def __init__(self, filename, **options):
        self.filename = filename
        super(LocalDataSource, self).__init__(**options)
    
    def get_file_path(self):
        #TODO return the proper filename or something
        return self.filename
    
    def get_data(self):
        path = self.get_file_path()
        source = open(path, 'r')
        adaptor = get_adaptor(self.options['format'])
        data = adaptor.deserialize(source)
        return data

class ZipfileDataSource(DataSource):
    def __init__(self, filename, archive, **options):
        self.filename = filename
        self.archive = archive
        super(ZipfileDataSource, self).__init__(**options)
    
    def get_file_path(self):
        return self.filename
    
    def get_data(self):
        path = self.get_file_path()
        source = self.archive.open(path)
        adaptor = get_adaptor(self.options['format'])
        data = adaptor.deserialize(source)
        return data

