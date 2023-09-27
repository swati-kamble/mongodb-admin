# Copyright (C) 2012 Costia Adrian,
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

from mongo.admin.dbadm import *
from mongo.admin.replication import Replication
from mongo.admin.mongodb import MongoDB,ConfigServer,MongoRouter
from mongo.admin.resplicaset import ReplicaSet
from mongo.admin.sharding import Shard

class Mongo:
    """
        Mongo operation
    """
    @staticmethod        
    def start(self, **kwargs):
        mongo_db = MongoDB(**kwargs)
        mongo_db.setParamaters()
        mongo_db.start()

    @staticmethod
    def stop(self):
        mongo_db = MongoDB()
        mongo_db.stop()

    @staticmethod
    def resume(self):
        mongo_db = MongoDB()
        mongo_db.resume()

    @staticmethod
    def suspend(self):
        mongo_db = MongoDB()
        mongo_db.suspend()
    
    @staticmethod
    def serverInfo(**kwargs):
        mongo_db = MongoDB(**kwargs)
        return mongo_db.serverInfo()

    @staticmethod
    def serverLog(**kwargs):
        mongo_db = MongoDB(**kwargs)
        return mongo_db.viewServerLog()

    @staticmethod
    def viewOperations(**kwargs):
        mongo_db = MongoDB(**kwargs)
        return mongo_db.viewOperations()

    @staticmethod
    def repair(database, **kwargs):
        mongo_db = MongoDB(**kwargs)
        return mongo_db.repair(database)

    @staticmethod
    def compactCollection(collection, **kwargs):
        mongo_db = MongoDB(**kwargs)
        return mongo_db.compactCollection(collection)
    
    @staticmethod
    def checkDataIntegrity(collection, **kwargs):
        mongo_db = MongoDB(**kwargs)
        return mongo_db.checkIntegrity(collection)
    
    @staticmethod
    def startMaster(db_path, **kwargs):
        master = Replication(is_master=True, **kwargs)
        master.dbPath(db_path)
        master.initParamaters()
        master.start()
        
    @staticmethod
    def startSlave(db_path, master, **kwargs):
        '''
            Mandatory parameter: master address
            Example:
                mongo = Mongo()
                mongo.startSlave("192.168.2.100:27020")
                
        '''
        slave = Replication(is_master=False, **kwargs)
        slave.dbPath(db_path)
        slave.source(master)
        slave.initParamaters()
        slave.start()
    
    @staticmethod
    def masterStatus(**kwargs):
        master = Replication(is_master=True, **kwargs)
        return master.masterInfo()

    @staticmethod
    def slaveStatus(**kwargs):
        slave = Replication(is_master=False, **kwargs)
        return slave.slaveInfo()
    
    @staticmethod
    def startReplicaSet(name,db_path, **kwargs):
        '''
           Example:
           
           mongo = Mongo()
           mongo.startReplicaSet(name="csign",db_path="/data/db/replica/r1/",bind_ip="172.16.101.229",port=27020)
           mongo.start()
        '''
        replSet = ReplicaSet(demonize=False, **kwargs)
        replSet.setName(name)
        replSet.dbPath(db_path)        
        replSet.initParamaters()
        replSet.start()
    
    @staticmethod
    def initiateReplicaSet(config, **kwargs):
        replSet = ReplicaSet(config=config, **kwargs)
        replSet.initiate()
    
    @staticmethod
    def statusReplicaSet(**kwargs):
        replSet = ReplicaSet(**kwargs)
        return replSet.getStatus()
    
    @staticmethod
    def isMaster(**kwargs):
        replSet = ReplicaSet(**kwargs)
        return replSet.isMaster()
        
    @staticmethod
    def addNode(host, **kwargs):
        '''
            Add new node 
        '''
        replSet = ReplicaSet(**kwargs)
        return replSet.addNode(host)
    
    @staticmethod
    def listNodes(**kwargs):
        replSet = ReplicaSet(**kwargs)
        return replSet.listNodes()

    @staticmethod
    def startConfigServer(db_path, **kwargs):
        '''
            Example:
            
            mongo = Mongo()
            mongo.startConfigServer(db_path="/data/db/replica/r1/",bind_ip="172.16.101.229",port=20000)
            
            This will produce:
                /usr/bin/mongod --configsvr --dbpath=/data/db/config/ --port 20000 --bind_ip=172.16.101.229
            
        '''
        config_srv = ConfigServer(db_path, **kwargs)
        config_srv.start()
    
    @staticmethod
    def startRouter(servers, **kwargs):
        '''
            Example:
            mongo = Mongo()
            mongo.startRouter(servers="172.16.101.229:27020",port=27021,bind_ip="172.16.101.229")
            
        '''
        mongo_router = MongoRouter(servers=servers, **kwargs)
        mongo_router.start()


    @staticmethod
    def statusRouter(**kwargs):
        '''
            Get router (mongos) status
        '''
        mongo_router = MongoRouter(**kwargs)
        return mongo_router.getStatus()

    @staticmethod
    def startShard(db_path, use_replica=False, servers=None, **kwargs):
        '''
            Example:
            
                1. Simple shard
                    mongo = Mongo()
                    mongo.startShard(db_path="/data/db/shard/s1/",bind_ip="172.16.101.229",port=20001)
                    
                2. With replica set enabled
                    mongo = Mongo()
                    mongo.startShard(
                        db_path="/data/db/shard/s1/",
                        use_replica=True,
                        servers="csing/alpha:27021,beta:27021",
                        bind_ip="172.16.101.229",
                        port=20001
                    )
            
        '''        
        shard = Shard(db_path=db_path, **kwargs)
        if use_replica and servers is not None:
            shard.useReplicaSet(servers)
        shard.initParamaters()
        shard.start()
    
    @staticmethod
    def addShardNode(servers, **kwargs):
        shard = Shard(**kwargs)
        return shard.addNode(servers)

    @staticmethod
    def shardDB(db, **kwargs):
        shard = Shard(**kwargs)
        return shard.shardDb(db)

    @staticmethod
    def shardCollection(collection, key, **kwargs):
        shard = Shard(**kwargs)
        return shard.shardCollection(collection, key)
    
    @staticmethod
    def listShards(**kwargs):
        shard = Shard(**kwargs)
        return shard.list()

    @staticmethod
    def statusShards(**kwargs):
        shard = Shard(**kwargs)
        return shard.getStatus()

    @staticmethod
    def moveTo(db, to_shard, **kwargs):
        shard = Shard(**kwargs)
        return shard.moveToPrimary(db, to_shard)

    @staticmethod
    def copyTo(from_db, to_db, from_host, **kwargs):
        mongo_db = MongoDB(**kwargs)
        return mongo_db.copyTo(from_db, to_db, from_host)

    @staticmethod
    def addUser(db, user, pwd):
        admin = DbAdmin()
        admin.addUser(user, pwd, db)
        
    @staticmethod
    def delUser(db, user):
        admin = DbAdmin()
        admin.delUser(user, db)

    @staticmethod
    def listDb(**kwargs):
        mongo_db = MongoDB(**kwargs)
        return mongo_db.listDatabases()
    
    @staticmethod
    def dropDb(db, **kwargs):
        mongo_db = MongoDB(**kwargs)
        return mongo_db.dropDb(db)

    @staticmethod
    def addIndex(collection, idx_name, idx_key, unique, drop_duplicates, **kwargs):
        mongo_db = MongoDB(**kwargs)
        return mongo_db.addIndex(collection, idx_name, idx_key, unique, drop_duplicates)

    @staticmethod
    def dropIndex(collection, idx_name, **kwargs):
        mongo_db = MongoDB(**kwargs)
        return mongo_db.dropIndex(collection, idx_name)
                             
    @staticmethod
    def getIndexes(database, **kwargs):
        mongo_db = MongoDB(**kwargs)
        return mongo_db.listIndexes(database)
    

        