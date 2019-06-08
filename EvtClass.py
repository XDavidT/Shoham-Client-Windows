import platform

class Evt:
    def __init__(self,id,time,type = None,cat = None,src = None, data = None):
        self.id = id
        self.time = time
        self.type = type
        self.cat = cat
        self.src = src
        self.data = data
        self.os = platform.system()

