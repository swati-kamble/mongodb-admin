# Copyright (C) 2012 Costia Adrian
# Created on Mar 9, 2012
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

from mongo.admin.mongodb import MongoDB
from mongo.utils.util import *
from mongo.utils.exceptions import *
from mongo.utils.const import *
from mongo.admin.dbadm import * 

class Server:
    pass

class ReplicaSet(MongoDB):
    '''
        Create replica set 
        
        srv_list = {
            server: "192.168.0.1:27018"
        }
        
    '''
    
    def __init__(self,name=None, db_path=None, config=None, **kwargs):
        super(ReplicaSet, self).__init__(**kwargs)
        
        self.setName(name)
        self.dbPath(db_path)
        if config is not None:
            self.config = config
            self.initiate()

    def addNode(self, host):
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.addNode(host)
        except Exception as exc:
            raise DBError(exc) 

    def listNodes(self):
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.getNodes()
        except Exception as exc:
            raise DBError(exc) 
    
    def setConfig(self, cfg):
        self.config = cfg
    
    def initiate(self):
        if self.config is None:
            raise DBError("Config not defined!")
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            initiate = dbadmin.initiate_replicaset(self.config)
        except Exception as exc:
            raise DBError(exc) 
    
    def checkType(self):
        '''
            Check to see if replicaSet is master
        '''
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            initiate = dbadmin.checkReplicaSetType()
            print initiate
        except Exception as exc:
            raise DBError(exc) 
    
    
    def isMaster(self):
        '''
            Check to see if host is master
        '''
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.isMaster()
        except Exception as exc:
            raise DBError(exc) 
        
    
    def getStatus(self):
        '''
            Get replica set status
        ''' 
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.getStatusReplicaSet()
        except Exception as exc:
            raise DBError(exc)

    def setName(self, name):
        '''
            Set replica set name
        '''
        if name is not None:
            setattr(self.params, REPLICA_SET, name)
