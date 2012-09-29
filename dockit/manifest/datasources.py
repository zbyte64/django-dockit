from common import DataSource, get_adaptor

from urllib2 import urlopen

class URLDataSource(DataSource):
    def __init__(self, url, **options):
        self.url = url
        super(URLDataSource, self).__init__(**options)
    
    def get_data(self):
        response = urlopen(self.url)
        adaptor = get_adaptor(self.options['format'])
        data = adaptor.deserialize(self, response)
        return data
    
    def to_payload(self, source_key, data):
        #TODO write data to url
        return {'source':source_key, 'url':self.url, 'format':self.format}

class InlineDataSource(DataSource):
    def __init__(self, data=None, **options):
        self.data = data
        super(InlineDataSource, self).__init__(**options)
    
    def get_data(self):
        return self.data
    
    def to_payload(self, source_key, data):
        self.data = data
        return {'source':source_key, 'data':data}

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
        data = adaptor.deserialize(self, source)
        return data
    
    def to_payload(self, source_key, data):
        #TODO write data to filename
        return {'source':source_key, 'filename':self.filename, 'format':self.format}

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
        data = adaptor.deserialize(self, source)
        return data
    
    def to_payload(self, source_key, data):
        #write data to options['archive']
        adaptor = get_adaptor(self.format)
        encoded_data = adaptor.serialize(data)
        self.archive.writestr(self.filename, encoded_data)
        
        return {'source':source_key, 'filename':self.filename, 'format':self.format}

