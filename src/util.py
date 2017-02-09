class DotDict(object):
    def __init__(self, d={}):
        self.d = d
    def __getattr__(self, key):
        return self.d[key]
    def __setattr(self, key, value):
        self.d[key] = value
