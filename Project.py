'''Module file for Project objects.  This controls the record structure that organizes the
project and the models generated.'''

from datetime import datetime

class AbstractModel(object):
    def __init__(self, datasets):
        self._datasets = datasets
        self._timestamp = str(datetime.now())
        
    def sample(self):
        '''Generates sample configurations from the model for initializing new trajectories.'''
        pass

    @property
    def timestamp(self):
        return self.timestamp

    @timestamp.set
    def update_timestamp(self):
        self._timestamp = str(datetime.now())

    def build_samples(self):
        '''Pure Virtual Method; this will require interacting with configurations that vary
        for different MD codes.'''
        raise NotImplementedError

class NAMDModel(AbstractModel):
    pass

class Project(object):
    def __init__(self):
        pass
