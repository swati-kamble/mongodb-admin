# Copyright (C) 2012 Costia Adrian
# Created on jan 10, 2012
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

import ConfigParser
import os.path
from mongo.utils.util import checkFile


class ConfigReader:
    
    READ_BINARY_MODE    = "rb"
    WRITE_BINARY_MODE   = "wb" 
    DELIMITER           = "="
    COMMENT             = "#"
    
    def __init__(self,filename):
        checkFile(filename)
        self.file       = filename
        self.content    = {}
    
    def read(self):
        with open(self.file,ConfigReader.READ_BINARY_MODE) as fl:
            for l in fl:
                print l
                # is comment ?
                if str(l).startswith(ConfigReader.COMMENT) == False:
                    line = str(l).rstrip(os.linesep).strip()
                    # split line by "delimitator"
                    if ConfigReader.DELIMITER in line:
                        (key,value) = line.split(ConfigReader.DELIMITER)
                        # add to dictionary
                        self.content[key] = value
    
    def get(self,key):
        if not self.content.has_key(key):
            raise KeyError("Key not found in config file.")
        return self.content.get(key)



class Config:
    """ Manipulate config file """
    _init_config          = False
    _config               = None
    _default_web_cfg_file = os.path.join(os.path.dirname(__file__), '..', '..', 'mongo', 'admin.conf')
    
    @staticmethod
    def init():
        
        # check for admin.cfg
        if os.path.isfile(Config._default_web_cfg_file):
            baseFilename = os.path.abspath(Config._default_web_cfg_file)
            
            # load config file
            Config._config = ConfigParser.RawConfigParser()
            Config._config.read(baseFilename)
            
            Config._init_config = True
            return Config._config
        else:
            # raise exception
            raise Exception("Config file admin.cfg not found in package")

    @staticmethod
    def getConfig():
        if Config._init_config == False:
            Config.init()
        
        return Config._config

    # read value from section
    @staticmethod
    def getValue(section,key):
        if Config._init_config == False:
            Config.init()
            
        if Config._config is None:
            raise Exception("Config object not initialized")
        return Config._config.get(section, key);
