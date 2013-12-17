'''Module file for Project objects.  This controls the record structure that organizes the
project and the models generated.'''

from datetime import datetime

class AbstractModel(object):
    def __init__(self, datasets):
        self._datasets = datasets
        self._timestamp = str(datetime.now())
        
    @property
    def timestamp(self):
        return self.timestamp

    def update_timestamp(self):
        self._timestamp = str(datetime.now())

    @property
    def datasets(self):
        return datasets

    #Dataset Handling Methods
    def register_new_dataset_pair(self, reduced_dataset_path, full_dataset_path):
        if reduced_dataset_path not in self._datasets:
            self._datasets.update({reduced_dataset_path : full_dataset_path})
        #Else: Raise exception?

    def register_new_raw_dataset(self, project_information):
        reduced_dataset_path, raw_dataset_path = self._process_raw_dataset(raw_dataset_path,
                                                                           project_information)
        self.register_new_dataset_pair(reduced_dataset_path, raw_dataset_path)

    def _process_raw_dataset(self):
        '''Pure Virtual method for processing a new raw dataset.'''
        raise NotImplementedError

    #Sampling Methods
    def sample(self):
        '''Generates sample configurations from the model for initializing new trajectories.'''
        pass

    def build_samples(self):
        '''Pure Virtual Method; this will require interacting with configurations that vary
        for different MD codes.'''
        raise NotImplementedError

class NAMDModel(AbstractModel):
    def _process_raw_dataset(self, raw_dataset_path):
        pass

    def build_samples(self):
        pass
        

class Project(object):
    def __init__(self):
        pass
