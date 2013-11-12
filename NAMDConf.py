## NAMDConf ##
'''Object model and functions for parsing NAMD config files.
This can be used to automatically interpret run information and
make decisions about burn-in times, naming conventions, and
mapping back to file information for extracting future run
conditions and writing out configuration files.'''

class NAMDConf:
    '''Object holding NAMD configuration file information.'''
    self._parameters = {}
    self._variables = {}
    
    def __init__(self, filename):
        self._parameters, self._variables = self.parse(filename)

    def parse(self, filename):
        pass

    def write(self, filename):
        pass

    def set_parameter(self, parameter_name, parameter_value):
        self._parameters[parameter_name] = parameter_value

    def set_variable(self, variable_name, variable_value):
        self._variables[variable_name] = variable_value
