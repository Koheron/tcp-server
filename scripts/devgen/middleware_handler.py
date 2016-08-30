# Generates a device description dictionnary and code fragments 
# from a tagged C++ header file
#
# (c) Koheron

import os
import time
import yaml
import string

from hpp_parser import parse_header, CSTR_TYPES

class MiddlewareHppParser:
    def __init__(self, hppfile):
        devices = parse_header(hppfile)
        self.raw_dev_data = devices[0]
        self.raw_dev_data["includes"] = [os.path.basename(hppfile)];
        self.device = self._get_device()

    def _get_template(self, ret_type):
        tokens = ret_type.split('<')

        if len(tokens) == 2:
            return tokens[1].split('>')[0].strip()
        else:
            return None

    def _get_device(self):
        device = {}
        device['operations'] = []
        device['raw_name'] = self.raw_dev_data['name']
        device['name'] = self.get_device_name()
        device['includes'] = self.raw_dev_data['includes']
        device['objects'] = [{
          'type': self.raw_dev_data['objects'][0]['type'],
          'name': '__' + self.get_device_name().lower()
        }]

        for op in self.raw_dev_data['operations']:
            device['operations'].append(self._format_operation(op))

        return device

    def get_device_name(self):
        ''' Build the device name from the class name '''
        raw_name = self.raw_dev_data['name']
        dev_name = []

        # Check whether there are capital letters within the class name
        # and insert an underscore before them
        for idx, letter in enumerate(raw_name):
            if idx > 0 and letter in list(string.ascii_uppercase):
                dev_name.append('_')

            dev_name.append(letter.upper())

        return ''.join(dev_name)

    def _format_operation(self, op):
        operation = {}
        operation['name'] = op['prototype']['name'].upper()
        operation['raw_name'] = op['prototype']['name']

        if 'flags' in op and len(op['flags']) > 0:
            operation['flags'] = op['flags']

        if len(op['prototype']['params']) > 0:
            operation['arguments'] = []

            for param in op['prototype']['params']:
                arg = {}
                arg['name'] = param['name']
                arg['type'] = param['type'].strip()
                self._format_argument(arg)
                operation['arguments'].append(arg)

        return operation

    def _format_argument(self, arg):
        if arg['type'][-1:] == '&': # Argument passed by reference
            arg['by_reference'] = True
            arg['type'] = arg['type'][:-2].strip()

        if arg['type'][:5] == 'const':# Argument is const
            arg['is_const'] = True
            arg['type'] = arg['type'][5:].strip()

class FragmentsGenerator:
    def __init__(self, parser):
        self.parser = parser

    def get_fragments(self):
        fragments = []

        for op in self.parser.raw_dev_data['operations']:
            op_name = op['prototype']['name'].upper()
            frag = {}
            frag['name'] = op_name
            frag['fragment'] = self.generate_fragment(op_name)
            fragments.append(frag)

        return fragments

    def generate_fragment(self, op_name):
        ''' Generate the fragment of an operation '''
        operation = self._get_operation_data(op_name)
        frag = []

        if operation['io_type']['value'] == 'WRITE':
            frag.append('    ' + self._build_func_call(operation) + ';\n')
            frag.append('    return 0;\n')
        elif operation['io_type']['value'] == 'READ':
            frag.append('    return SEND('+ self._build_func_call(operation) + ');\n')
        elif operation['io_type']['value'] == 'READ_CSTR':
            if operation['prototype']['ret_type'] not in CSTR_TYPES:
                raise ValueError('I/O type READ_CSTR expects a char*. Found '
                                 + operation['prototype']['ret_type'] + '.\n')

            frag.append('    return SEND_CSTR('
                        + self._build_func_call(operation) + ');\n')

        return frag

    def _get_operation_data(self, op_name):
        for op in self.parser.raw_dev_data["operations"]:
            if op["prototype"]["name"].upper() == op_name:
                return op
        raise ValueError("Unknown operation " + op_name)

    def _build_func_call(self, operation):
        obj_name = self.parser.device["objects"][0]["name"]
        func_name = operation["prototype"]["name"]
        call = "THIS->" + obj_name + "." + func_name + "("
        
        for count, param in enumerate(operation["prototype"]["params"]):
            if count == 0:
                call += "args." + param["name"]
            else:
                call += ", args." + param["name"]

        call += ")"
        return call
