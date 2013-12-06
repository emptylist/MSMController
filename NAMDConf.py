## NAMDConf ##
'''Object model and functions for parsing NAMD config files.
This can be used to automatically interpret run information and
make decisions about burn-in times, naming conventions, and
mapping back to file information for extracting future run
conditions and writing out configuration files.'''

## Copyright 2013 James Crooks
## Released under the MIT License

from util import DictDiff
from datetime import date, datetime
from collections import deque
from functools import wraps
import re

def _tokenize(raw_lines):
    '''Function that accepts a list of lines as read in by readlines()
    and returns a deque of tokens for a NAMD Config file.'''
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
    '''Class for building parser objects.  The parser object is designed to parse
    a list of lines read from a text file exactly once.  The parser has no "public"
    methods, and should only be used to parse text upon initialization.  The parser
    is modeled as a Finite State Machine, and should be discarded immediately upon
    finishing because it is stateful and messy as all hell. The parse function
    builds a parser, uses it to parse text, and returns the parsed values, allowing
    the GC to collect the parser as it goes out of scope. Thus parse acts as a
    functional interface, allowing us to wrap the messy statefulness of the FSM
    behind a functional interface.'''
    ## "One does not simply read the source code"
    ## Here begins a mess
    ## but at least it's tightly contained
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
        if self._accepting:
            self._binding_variable = True

    def _if(self):
        if self._accepting:
            self._conditional = True

    def _open_brace(self):
        if self._conditional:
            self._conditional_scope = True
            self._conditional = False
        else:
            self._binding_scope = True

    def _close_brace(self):
        if self._conditional_scope:
            try:
                self._accepting = all(map(int, self._token_buffer))
            except:
                print("Error encounter on line " +
                      self._line_number + ". Ignoring following scope.\n")
                self._accepting = False
            self._conditional_scope = False
        else:
            self._accepting = True
            self._binding_scope = False

    def _newline(self):
        self._binding_variable = False
        self._current_name = None
        self._num_values_to_bind = 0
        self._value_token_buffer = []
        self._line_number += 1

    def _bind_name(self):
        self._current_name = self._current_token
        self._num_values_to_bind = self._parameter_data_size.get(self._current_token, 1)
    
    def _bind_value(self):
        self._num_values_to_bind = max(self._num_values_to_bind - 1, 0)
        self._value_token_buffer.append(self._current_token)
        if not self._num_values_to_bind:
            if self._binding_variable:
                self.variables.update({self._current_name : " ".join(self._value_token_buffer)})
            else:
                self.parameters.update({self._current_name : " ".join(self._value_token_buffer)})
            self._value_token_buffer = []

    def _dispatch_binding(self):
        if self._accepting:
            if self._conditional_scope:
                self._token_buffer.append(self._current_token)
            elif self._current_name:
                self._bind_value()
            else:
                self._bind_name()

    def _parse_tokens(self):
        self._binding_scope = False
        self._conditional_scope = False
        self._conditional = False
        self._accepting = True
        self._binding_variable = False
        self._current_name = None
        self._line_number = 0
        self._token_buffer = []
        self._value_token_buffer = []
        self._num_values_to_bind = 0
        while self._tokens:
            self._current_token = self._tokens.popleft()
            self._command_tokens.get(self._current_token, self._dispatch_binding)()

def parse(filename):
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
            self._readfrom = None
        else:
            self._parameters, self._variables = parse(filename)
            self._readfrom = str(filename)
        self._required_parameters = [
              "numsteps"
            , "coordinates"
            , "structure"
            , "parameters"
            , "exclude"
            , "outputname"]
        if verbose:
            self.verbose_on()
        else:
            self.verbose_off()
        self._log = []

    @property
    def log(self):
        return self._log

    #The logger function.  It's questionable whether making it into some sort of insane
    #'hidden method' decorator is overengineering, just stupid, or actually a good call.
    #I want the overall command script to do most of the logging, however I think that
    #having the config files log their own histories internally is particularly valuable here,
    #in addition to any other logging the command script does.
    def logger(func):
        """The logger function.  It's questionable whether making it into some sort of insane
        'hidden method' decorator is overengineering, just stupid, or actually a good call.
        I want the overall command script to do most of the loggin, however, I think that
        having the config files log their own histories internally is particularly valuable here,
        in addition to any other logging the command script does."""
        @wraps(func)
        def wrapper(self, *args):
            old_parameters = self._parameters
            old_variables = self._variables
            timestamp = str(datetime.datetime.now())
            func(self, *args)
            if DictDiffer(old_parameters, self._parameters).changes:
                self._log.append((timestamp,
                                  DictDiffer(old_parameters, self._parameters).changes))
            if DictDiffer(old_parameters, self._parameters).changes:
                self._log.append(DictDiffer(old_variables, self._parameters).changes)
        return wrapper

    @property
    def parameters(self):
        return self._parameters

    @logger
    def set_parameter(self, k, v):
        self._parameters[k.tolower()] = v

    @logger
    def remove_parameter(self, k):
        self._parameters.pop(k.tolower(), None)

    @property
    def variables(self):
        return self._variables
    
    @logger
    def set_variable(self, k, v):
        self._variables[k] = v
        
    @logger
    def remove_variable(self, k):
        self._variables.pop(k, None)

    @property
    def verbose(self):
        return self._verbose

    def verbose_on(self):
        self._verbose = True

    def verbose_off(self):
        self._verbose = False

    #Here follows some 'properties' exposing particularly useful parameters
    #I think this makes me an OO-whore for programming this way.
    #May the Gods of Functional Programming forgive me.
    
    @property
    def dcd_file(self):
        base_name = self.parameters.get("outputname", None)
        if base_name:
            return str(base_name) + ".dcd"
        return none

    @property
    def psf_file(self):
        return self.parameters.get("structure", None)

    @property
    def timestep(self):
        return self.parameters.get("timestep", None)

    @property
    def total_time(self):
        timestep = self.parameters.get("timestep", None)
        numsteps = self.parameters.get("numsteps", None)
        if timestep and numsteps:
            return timestep * numsteps
        return None

    #Methods that actually do things

    def _write_warnings(self):
        for key in self._required_parameters:
            if key not in self._parameters:
                print("Warning! Did not set necessary parameter " + key + " in config file.")

    def write(self, filename):
        try:
            with open(filename, 'w') as wf:
                wf.write("## NAMD Configuration File, written by MSMControl on "
                         + date.today() + "\n")
                if self._variables:
                    wf.write("## Script Variables\n")
                    for key in self._variables:
                        wf.write("set " + key + " " + self._variables[key] + "\n")
                if self._verbose:
                    self._write_warnings()
                wf.write("## NAMD Parameters\n")
                for key in self._parameters:
                    wf.write(key + "  " + self._parameters[key] + "\n")
                if self._readfrom:
                    wf.write("##LOG: Initial parameters drawn from file "+ self._readfrom + "\n")
                for record in self._log:
                    wf.write("#LOG: " + " ".join(filter(None, [record.timestamp,
                            record.type, record.name, record.action, record.value]) + "\n")
        except:
            print("Failed to open " + filename + " for writing.")
