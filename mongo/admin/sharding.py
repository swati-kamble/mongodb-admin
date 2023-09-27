# Copyright (C) 2012 Costia Adrian
# Created on Mar 12, 2012
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

class Shard(MongoDB):
    '''
        Create Shard Servers
    
            A shard server consists of a mongod process or a replica set of mongod processes. 
            For production, use a replica set for each shard for data safety and automatic failover.
            To get started with a simple test, we can run a single mongod process per shard,
            as a test configuration doesn't demand automated failover.
            
            More details at http://www.mongodb.org/display/DOCS/Configuring+Sharding
            
        Example:
        
            1. Start shard:
            
                shd = Shard(db_path="/data/db/sharding/s1/",bind_ip="10.179.65.220",port=27020)
                # enable shard with replica set
                shd.useReplicaSet("csign/10.179.65.221:27020") 
                shd.initParamaters()
                shd.start()
                
            2. Start shard:
            
                shd = Shard(bind_ip="10.179.65.220",port=27020)
                shd.dbPath("/data/db/sharding/s1/")
                shd.useReplicaSet("csign/10.179.65.221:27020") 
                shd.initParamaters()
                shd.start()
            
            3. Shard database
            
                shd = Shard()
                shd.shardDb("test")
            
            4. Shard collection

                shd = Shard()
                shd.shardCollection("test.foo.empathy",{empathyse: 1})
            
            5. Add node - run this command on router:
                shd = Shard()
                shd.addNode("shard_001","localhost:2000")
                 -or -
                shd.addNode("shard_001","csign/server1,server2")
                    - where csign is the replica name
            
            6. Remove shard:
                shd = Shard()
                shd.removeShard("shard_001")
                shd.shutdownShard("shard_001")
                
    '''
    def __init__(self, db_path=None, port=27018, **kwargs):
        super(Shard, self).__init__(port=port, **kwargs)
        # set default port
        # enable sharding
        setattr(self.params, SHARD_SERVER, True)
        self.dbPath(db_path)

    
    def useReplicaSet(self, replica_set):
        '''
            For failover use sharding with replicaSet
            Example:            
                sh = Shard(...)
                sh.useReplicaSet("foo/server1:port,server2:port")
                
                - to enable sharding use sh.addNode("foo/server1:port,server2:port")
        '''
        setattr(self.params, REPLICA_SET, replica_set)
    
    def dbPath(self, path):
        if path is not None:
            if not path_exists(path):
                makedirs(path)
            self.data_path = path

    def addNode(self, servers):
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.addShardNode(servers)
        except Exception as exc:
            raise DBError(exc) 
    
    def removeNode(self, name):
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            shard = dbadmin.removeShard(name)
        except Exception as exc:
            raise DBError(exc) 
    
    def shardDb(self, db):
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.enableShardingOnDB(db)
        except Exception as exc:
            raise DBError(exc) 
    
    def shardCollection(self, collection_name, key):
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.shardCollection(collection_name, key)
        except Exception as exc:
            raise DBError(exc) 
    
    def moveToPrimary(self, db, to_shard):
        '''
            !Important: 
                - This command is only available on a sharded system through "mongos".
                - This command is meant to be run on an offline system and only in the case where you need to remove a shard.

            Example:
                - this will move db "hat" to shard 172.16.101.229:27021
                    shard = Shard(**args)
                    shard.moveToPrimary("hat","172.16.101.229:27021")
                        -> response: {u'ok': 1.0, u'primary ': u'shard0001:172.16.101.229:27021'}
                        -> in mongos console:
                                Thu Mar 15 17:19:05 [conn7] distributed lock 'hat-movePrimary/L-MOB-COSTIA:27017:1331824364:41' acquired, ts : 4f6208693b5dcce9c98c24a3
                                Thu Mar 15 17:19:05 [conn7] movePrimary:  dropping hat from old
                                Thu Mar 15 17:19:05 [conn7] distributed lock 'hat-movePrimary/L-MOB-COSTIA:27017:1331824364:41' unlocked.

        '''
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.moveToPrimary(db, to_shard)
        except Exception as exc:
            raise DBError(exc) 
        
    def splittingChunks(self, collection, query):
        '''
            Note: in development
        '''
        pass
    
    def list(self):
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.listShards()
        except Exception as exc:
            raise DBError(exc) 
    
    def getStatus(self):
        '''
            Get shard status
        '''
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.shardStatus()
        except Exception as exc:
            raise DBError(exc) 