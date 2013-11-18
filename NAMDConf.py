## NAMDConf ##
'''Object model and functions for parsing NAMD config files.
This can be used to automatically interpret run information and
make decisions about burn-in times, naming conventions, and
mapping back to file information for extracting future run
conditions and writing out configuration files.'''

## Copyright 2013 James Crooks
## Released under the MIT License

from datetime import date
from collections import deque
import re

def _tokenize(raw_lines):
    '''Function that accepts a list of lines as read in by readlines()
    and returns a list of tokens for a NAMD Config file.'''
    def clean_comment(s):
        return s[:(s.find('#'))]
    cleaned_lines = map(clean_comment, raw_lines)
    tokens = deque()
    for line in cleaned_lines:
        sline = re.split('([{}])|[\s]', line)
        for dummy_index in range(sline.count(None)):
            sline.remove(None)
        for entry in sline:
            tokens.append(entry.lower())
        tokens.append("newline")
    return tokens
    
class NAMDConfParser(object):
    def __init__(self, raw_lines):
        self.parameters = {}
        self.variables = {}
        self._command_tokens = {
              "set": self._set
            , "if": self._if
            , "{": self._open_brace
            , "}": self._close_brace
            , "newline": self._newline
            }
        self._parameter_data_size = {
              "cellbasisvector1" : 3
            , "cellbasisvector2" : 3
            , "cellbasisvector3" : 3
            , "cellorigin"       : 3
            }
        self._tokens = _tokenize(raw_lines)
        self._parse_tokens(tokens)

    def _set(self):
        pass

    def _if(self):
        pass

    def _open_brace(self):
        pass

    def _close_brace(self):
        pass

    def _newline(self):
        self._binding_variable = False
        self._current_name = None
        self._line_number += 1

    def _bind_parameter(self):
        pass
    
    def _parse_tokens(self):
        self._nested_scope = False
        self._conditional = False
        self._accepting = True
        self._binding_variable = False
        self._current_name = None
        self._line_number = 0
        while self._tokens:
            current_token = self._tokens.popleft()
            self._command_tokens.get(current_token, self._bind_parameter)()

def _parse(filename):
    try:
        with open(filename, 'r') as f:
            ind = f.readlines()
    except Exception, e:
        e.message(filename + " couldn't be opened.  Parsing failed.")
    parser = NAMDConfParser(ind)
    return parser.parameters, parser.variables

class NAMDConf(object):
    '''Object holding NAMD configuration file information.'''
    def __init__(self, filename = None, verbose = True):
        if filename is None:
            self._parameters = {}
            self._variables = {}
        else:
            self._parameters, self._variables = self._parse(filename)
        self._required_parameters = [
              "numsteps"
            , "coordinates"
            , "structure"
            , "parameters"
            , "exclude"
            , "outputname"]
        ''' ##YAGNI values##
        self._input_file_parameters = [
              "coordinates"
            , "structure"
            , "parameters"
            , "paraTypeXplor"
            , "paraTypeCharmm"
            , "velocities"
            , "binvelocities"
            , "bincoordinates"
            , "cwd"
            ]
        self._output_file_parameters = [
              "outputname"
            , "binaryoutput"
            , "restartname"
            , "restartfreq"
            , "restartsave"
            , "binaryrestart"
            , "DCDfile"
            , "DCDfreq"
            , "DCDUnitCell"
            , "velDCDfile"
            , "velDCDfreq"
            ]
        self._standard_output_parameters = [
              "outputEnergies"
            , "mergeCrossterms"
            , "outputMomenta"
            , "outputPressure"
            , "outputTiming"
            ]
        self._timestep_parameters = [
              "numsteps"
            , "timestep"
            , "firsttimestep"
            , "stepspercycle"
            ]
        self._simulation_space_partitioning_parameters = [
              "cutoff"
            , "switching"
            , "limitdist"
            , "pairlistdist"
            , "splitPatch"
            , "hgroupCutoff"
            , "margin"
            , "pairlistMinProcs"
            , "pairlistsPerCycle"
            , "outputPairLists"
            , "pairlistShrink"
            , "pairlistGrow"
            , "pairlistTrigger"
            ]
        self._basic_dynamics_parameters = [
              "exclude"
            , "temperature"
            , "COMmotion"
            , "zeroMomentum"
            , "dielectric"
            , "nonbondedScaling"
            , "1-4scaling"
            , "vdwGeometricSigma"
            , "seed"
            , "rigidBonds"
            , "rigidTolerance"
            , "rigidIterations"
            , "rigidDieOnError"
            , "useSettle"
            ]
        '''
        if verbose:
            self.verbose_on()
        else:
            self.verbose_off()

    @property
    def parameters(self):
        return self._parameters

    def set_parameter(self, k, v):
        self._parameters[k.tolower()] = v

    def remove_parameter(self, k):
        self._parameters.pop(k.tolower(), None)

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

    def _parse(self, filename):
        try:
            with open(filename, 'r') as f:
                ind = f.readlines()
        except Exception, e:
            e.message("File " + filename + " can't be located. File parsing failed.")
        parser = NAMDConfParser(ind)
        return parser.parameters, parser.variables
    """
    ##Old Code, that does not properly work
        parameters = {}
        variables = {}
        ## some flags controlling primitive nested controls
        nested_brace = False

        accept_state = True
        for line in ind:
            if not line[0] == '#':
                text = line.split()
                if text[0] == '}':
                    nested_brace = False
                    accept_state = True
                else if (open_brace and accept_state):
                    
                if text[0] = set:
                    variables[text[1]] = text[2]
                else:
                    parameters[text[0]] = text[1]
        return parameters, variables
    """
    
    def _write_warnings(self):
        for key in self._required_parameters:
            if key not in self._parameters:
                print("Warning! Did not set necessary parameter " + key + " in config file.")

    def write(self, filename):
        try:
            wf = open(filename, 'w')
        except:
            print("Failed to open " + filename + " for writing.")
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

