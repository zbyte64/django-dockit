class DotPathNotFound(Exception):
    def __init__(self, message, traverser=None):
        Exception.__init__(self, message)
        self.traverser = traverser
