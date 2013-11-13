## NAMDConf ##
'''Object model and functions for parsing NAMD config files.
This can be used to automatically interpret run information and
make decisions about burn-in times, naming conventions, and
mapping back to file information for extracting future run
conditions and writing out configuration files.'''

## Copyright 2013 James Crooks
## Released under the MIT License

from datetime import date

class NAMDConf(object):
    '''Object holding NAMD configuration file information.'''
    def __init__(self, filename = None, verbose = True):
        if filename is None:
            self._parameters = {}
            self._variables = {}
        else:
            self._parameters, self._variables = self._parse(filename)
        self._required_parameters = []
        if verbose:
            self.verbose_on()
        else:
            self.verbose_off()

    @property
    def parameters(self):
        return self._parameters

    def set_parameter(self, k, v):
        self._parameters[k] = v

    def remove_parameter(self, k):
        self._parameters.pop(k, None)

    @property
    def variables(self):
        return self._variables

    def set_variable(self, k, v):
        self._variables[k] = v
        
    def remove_variable(self, k):
        self._variables.pop(k, None)

    @property
    def verbose(self):
        return self._verbose

    def verbose_on(self):
        self._verbose = True

    def verbose_off(self):
        self._verbose = False

    def _parse(self):
        try:
            with open(filename, 'r') as f:
                ind = f.readlines()
        except:
            print("File " + filename + "can't be located. File parsing failed.")

        parameters = {}
        variables = {}
        for line in ind:
            if not line[0] == '#':
                text = line.split()
                if text[0] = set:
                    variables[text[1]] = text[2]
                else:
                    parameters[text[0]] = text[1]
        return parameters, variables

    def _write_warnings(self):
        for key in self._required_parameters:
            if key not in self._parameters:
                print("Warning! Did not set necessary parameter " + key + " in config file.")

    def write(self, filename):
        try:
            wf = open(filename, 'w')
        except:
            print("Failed to open " + filename + "for writing.")
        wf.write("## NAMD Configuration File, written by MSMControl on " + date.today() + "\n")
        if self._variables:
            wf.write("## Script Variables\n")
            for key in self._variables:
                wf.write("set " + key + " " + self._variables[key] + "\n")
        if self._verbose:
            self._write_warnings()
        for key in self._parameters:
            wf.write(key + "  " + self._parameters[key] + "\n")
        wf.close()
        
