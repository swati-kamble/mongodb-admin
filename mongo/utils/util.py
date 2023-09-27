# Copyright (C) 2012 Costia Adrian
# Created on Mar 5, 2012
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import imp
import platform
import os
import sys
import inspect
from socket import error, socket, AF_INET, SOCK_STREAM
from mongo.utils.const import *


def checkHost(host, port):
    s = socket(AF_INET, SOCK_STREAM)
    try:
        try:
            s.connect((host, port))
            return True
        except (IOError, error):
            return False
    finally:
        s.close()

def parse_hosts(srv_list):
    servers = srv_list.split(COMMA)
    print "Checking host(s)...Please wait few moments."
    for server in servers:
        (host, port) = server.split(":")
        if port is None:
            port = 20000
        # check host
        print "Host %s:%s " % (host, port) 
        if not checkHost(host, int(port)):
            print "Host %s:%s is down! " % (host, port)
            sys.exit(2)
        else:
            print "Host %s:%s is up! " % (host, port)
    return servers


def checkFile(file):
    '''
        Check file
    '''
    if not os.path.isfile(file):
        raise IOError("Can't find file " + str(file))

def path_exists(path):
    '''
        Check path
    '''
    if os.path.exists(path):
        return True
    return False
   

def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

def logical_drives():
    import string
    from ctypes import windll

    logical_drives = []
    bmask = windll.kernel32.GetLogicalDrives() 
    for drv in string.uppercase:
        if bmask & 1:
            logical_drives.append(drv)
        bmask >>= 1
    return logical_drives


def whereis(find_file):
    '''
        Locate file on drive
    '''
    drives = logical_drives()
    for drv in drives:
        print "Reading drive >> " + drv + "...Please wait few seconds."
        for path, dirs, files in os.walk(drv + ":\\"):
            for file in files:
                if find_file in file:
                    # set file location in config file
                    return path

class Options(object):
    pass

def has_method(clazz, method):
    class_methods = inspect.getmembers(clazz, inspect.ismethod)
    if not isinstance(class_methods, list):
        raise TypeError, "clazz method must be a List instance"

    if len(class_methods) > 0:
        for class_method in class_methods:
            if method in class_method[0]: # where "method" is the method in clazz
                return True
    return False

def inspect_clazz(clazz):
    methods = inspect.getmembers(clazz, inspect.ismethod)
    methods_map = {}
    for method in methods:
        methods_map[method[0]] = method[1]
    return methods_map    

def dict2Class(data):
    '''
        Transform dictionary in class 
    '''
    if isinstance(data, list):
        data = [dict2Class(val) for val in data]
    if not isinstance(data, dict):
        return data
    
    options = Options()
    for key in data:
        options.__dict__[key] = dict2Class(data[key])
    return options

def attr2Class(clazz, data):
    '''
        Transform dictionary in class 
    '''
    if isinstance(data, list):
        data = [attr2Class(clazz, val) for val in data]
    if not isinstance(data, dict):
        return data
    for key in data:
        if data[key] is not None:
            clazz.__dict__[key] = attr2Class(clazz, data[key])
    return clazz

def setParam(params, key, value=True):
    if to_bool(value):
        setattr(params, key, value)
    else:
        delattr(params, key)
    
def to_bool(value):
    """
       Converts 'something' to boolean. Raises exception for invalid formats
           Possible True  values: 1, True, "1", "TRue", "yes", "y", "t"
           Possible False values: 0, False, None, [], {}, "", "0", "faLse", "no", "n", "f", 0.0, ...
    """
    if isinstance(value, bool):
        return value
    if str(value).lower() in ("yes", "y", "true",  "t", "1"): return True
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"): return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))

def to_param(param, value):
    return "".join(["--", param, "=", value])

def to_option(param):
    return "".join(["--", param])

def extract_parameters(clazz):
    _params = []
    clazz_params = clazz.__dict__
    if len(clazz_params) > 0:
        for (key, value) in clazz_params.items():
            param = None
            if isinstance(value, bool):
                if value:
                    param = to_option(key)                
            else:
                param = to_param(key, str(value))
            if param is not None:
                _params.append(param)
    return _params
    
def array2params(array):
    '''
        Transform a dictionary to param 
    '''
    return ''.join(' %s' % (param) for param in array)

def getParamValue(arg, search_key):
    try:
        if arg.find(search_key) != -1:
            if arg.find(EQUAL) == -1:
                raise Exception(" '=' not found in key! Please use key=value ")
            uargs = arg.split("=")
            return uargs[1]
        else:
            return arg
    except Exception:
        return None