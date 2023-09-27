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

from mongo.utils.exceptions import *
from mongo.utils.const import *
from mongo.admin.mongodb import MongoDB
from mongo.admin.dbadm import *

class Replication(MongoDB):
    
    def __init__(self,is_master=False, **kwargs):
        super(Replication, self).__init__(**kwargs)
        '''
            set server type: master -or- slave
        '''
        self.isMaster(is_master)
    
    def isMaster(self,enabled):
        '''
            Designate this server as a master in a master-slave setup
            -or-
            Designate this server as a slave in a master-slave setup
        '''
        if not isinstance(enabled, bool):
            raise NotBoolean
        if enabled:
            setattr(self.params, MASTER, enabled)
        else:
            setattr(self.params, SLAVE, True)
            
    def source(self, master_server):
        '''
            Specify the source (master) for a slave instance
        '''
        if hasattr(self.params, MASTER):
            raise DBError("This option is available only when the server is slave")
        setattr(self.params, SERVER_SOURCE, master_server)
    
    def setArbiter(self,server_arbiter):
        '''
          Address of arbiter server  
        '''
        setattr(self.params, SERVER_ARBITER, server_arbiter)
    
    def replicateOnlyDB(self, db):
        '''
            Slave only: specify a single database to replicate
        '''
        if self.params.is_master:
            raise DBError("This option is available only when the server is slave")
        setattr(self.params, REPLICATE_ONLY_DB, db)

    
    def autoReSync(self, enabled):
        '''
            Automatically resync if slave data is stale
        '''
        if not isinstance(enabled, bool):
            raise NotBoolean
        setattr(self.params, AUTO_RESYNC, enabled)
        
    def oplogSize(self, sizeMB):
        '''
            Replication uses an operation log ("oplog") to store write operations. These operations replay asynchronously
            on other nodes.The length of the oplog is important if a secondary is down. The larger the log, the longer 
            the secondary can be down and still recover. Once the oplog has exceeded the downtime of the secondary, 
            there is no way for the secondary to apply the operations; it will then have to do a full synchronization of the data from the primary.
            By default, on 64 bit builds, the oplog is allocated to 5% of disk space. Generally this is a reasonable setting.
            The oplog is a capped collection, and fixed size once allocated. Once it is created it is not easy to change without losing the existing data.
            This will be addressed in future versions so that it can be extended.
            The mongod --oplogSize command line parameter sets the size of the oplog. Changing this parameter after the oplog is created does not change 
            the size of your oplog.

            This collection is named:
                local.oplog.$main for master/slave replication
                local.oplog.rs for replica sets
        '''
        setattr(self.params, OPLOG_SIZE, sizeMB)
           
    def slaveDelay(self, seconds):
        if not isinstance(seconds, int):
            raise NotInt()
        setattr(self.params, SLAVE_DELAY, seconds)

    
    def slaveInfo(self):
        '''
            alternative to: db.printSlaveReplicationInfo()
        '''
        try:
            admin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return admin.showSlaveStatus()
        except Exception as exc:
            raise DBError(exc)
        
    def masterInfo(self):
        '''
            alternative to : db.printReplicationInfo()
        '''
        try:
            admin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return admin.showMasterStatus()
        except Exception as exc:
            raise DBError(exc)