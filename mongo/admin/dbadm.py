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

import json
from mongo.utils.exceptions import DBError
from bson.son import SON
from pymongo import *
from mongo.utils.const import *

class Host:
    def __init__(self, id, host):
        self._id  = id
        self.host = host 

class DbAdmin:
    CMD_SHUTDOWN                    = "shutdown"
    CMD_INITIATE_REPLICASET         = "replSetInitiate"
    CMD_RECONFIG_REPLICASET         = "replSetReconfig"
    CMD_REPLICATION_MASTER_STATUS   = "printReplicationInfo"
    CMD_REPLICATION_SLAVE_STATUS    = "printSlaveReplicationInfo"
    CMD_REPLICA_SET_STATUS          = "replSetGetStatus"
    CMD_SERVER_STATUS               = "serverStatus"
    CMD_VALIDATE                    = "validate"
    CMD_REPAIR_DATABASE             = "repairDatabase"
    CMD_COMPACT_COLLECTION          = "compact"
    CMD_REPLICA_SET_IS_MASTER       = "isMaster"
    CMD_ADD_NODE                    = "add"
    CMD_ADD_SHARD                   = "addshard"
    CMD_REMOVE_SHARD                = "removeshard"
    CMD_NAME                        = "name"
    CMD_LIST_SHARDS                 = "listshards"
    CMD_ENABLE_SHARDING             = "enablesharding"
    CMD_SHARD_COLLECTION            = "shardcollection"
    CMD_KEY                         = "key"
    CMD_MOVE_PRIMARY                = "movePrimary"
    CMD_SET_NAME                    = "setName"
    CMD_TO                          = "to"
    CMD_COPY_DB                     = "copydb"
    CMD_CLONE_DB                    = "clone"
    CMD_LIST_DATABASES              = "listDatabases"
    CMD_DROP_DATABASE               = "dropDatabase"
    CMD_DROP_INDEX                  = "deleteIndexes"
    CMD_VIEW_SYSTEM_LOG             = "getLog"
    FROM_HOST                       = "fromhost"
    FROM_DB                         = "fromdb"
    TO_DB                           = "todb"
    GLOBAL_LOG                      = "global"
    
    def __init__(self, server=None, port=None):
        if server is None:
            server = "localhost"
        if port is None:
            port = 27017
        self.cnx   = Connection(host=server, port=port)
        self.admin = self.cnx.admin 
    
    def _executeCommand(self, command):
        try:
            return self.admin.command(command)
        except Exception as exc:
            raise DBError(str(exc))
    
    def shutdown(self):
        self._executeCommand(DbAdmin.CMD_SHUTDOWN)
    
    def viewCurrentOperation(self):
        try:
            db = self.cnx.db['$cmd.sys.inprog']
            return db.find_one()
        except Exception,exc:
            raise DBError(str(exc))
        
    def checkDataIntegrity(self, collection):
        '''
            You can use the validate command on to check if the contents of a collection are valid.
        '''
        if collection.find(DOT) == -1:
            raise DBError("Database or collections not specified. Use checkDataIntegrity(<db.colection>) ")
        res = collection.split(DOT)
        try:
            database   = res[0]
            collection = res[1]
            db = self.cnx[database]
            return db.command({DbAdmin.CMD_VALIDATE:collection})
        except Exception, exc:
            raise DBError(str(exc))
        
    def repairDB(self, database):
        if not isinstance(database, basestring):
            raise TypeError("Database must be an instance of (Database, str, unicode)")
        
        try:
            db = self.cnx[database]
            return db.command({DbAdmin.CMD_REPAIR_DATABASE:1})
        except Exception, exc:
            raise DBError(str(exc))
    
    def compactCollection(self, collection):
        '''
            The compact command compacts and defragments a collection. Indexes are rebuilt at the same time.
            It is conceptually similar to repairDatabase, but works on a single collection rather than an entire database.
            
            More details at http://www.mongodb.org/display/DOCS/Compact+Command
        '''
        if collection.find(DOT) == -1:
            raise DBError("Database or collections not specified. Use checkDataIntegrity(<db.colection>) ")
        res = collection.split(DOT)
        try:
            database   = res[0]
            collection = res[1]
            db = self.cnx[database]
            return db.command({DbAdmin.CMD_COMPACT_COLLECTION:collection})
        except Exception,exc:
            raise DBError(str(exc))
        
    def getLog(self):
        '''
            View system log
        '''
        return self._executeCommand({DbAdmin.CMD_VIEW_SYSTEM_LOG:DbAdmin.GLOBAL_LOG})
    
    def addUser(self, username, password, database='admin'):
        try:
            db = self.cnx[database]
            db.add_user(username, password)
        except Exception as exc:
            raise DBError(str(exc))

    def delUser(self, username, database='admin'):
        try:
            db = self.cnx[database]
            db.remove_user(username)
        except Exception as exc:
            raise DBError(str(exc))

    def setChunkSize(self, port):
        try:
            config = Connection('localhost', int(port)).config
            config.settings.save({'_id' : 'chunksize', 'value' : self.CHUNK_SIZE}, safe=True)
        except Exception as exc:
            raise DBError(str(exc))
    
    def initiate_replicaset(self, config):
        '''
            Config example:
            {
                _id : csign,
                members : [
                    {_id : 0, host : <host0>},
                    {_id : 1, host : <host1>},
                    ...
                ]
            }
            More example at http://www.mongodb.org/display/DOCS/Replica+Set+Configuration
            
            Example:
            dbadmin = DBAdmin()
            
            cfg = {
                _id: 'csign', members: [
                          {_id: 0, host: '192.168.176.128:27017'},
                          {_id: 1, host: '192.168.176.129:27017'},
                          {_id: 2, host: '192.168.176.130:27017'}]
                }    
            dbadmin.initiate_replicaset(cfg)
            
        '''
        if not isinstance(config, dict):
            raise Exception("Not dictionary!")
        
        cmd = {DbAdmin.CMD_INITIATE_REPLICASET : config }
        return self._executeCommand(cmd)        

    def serverInfo(self):
        '''
            Get server status
        '''
        return self._executeCommand(DbAdmin.CMD_SERVER_STATUS);
    
    def isMaster(self):
        '''
                 { 
                    'me': '172.16.101.229:27017',
                    'ismaster': True,
                    'ok': 1.0, 
                    'setName': 'csign', 
                    'primary': '172.16.101.229:27017', 
                    'hosts': [
                              '172.16.101.229:27017'
                             ], 
                     'maxBsonObjectSize': 16777216, 
                     'passives': ['172.16.101.229:27018'], 
                     'secondary': False
                 }            
        '''
        try:
            return self._executeCommand(DbAdmin.CMD_REPLICA_SET_IS_MASTER)
        except Exception, exc:
            raise DBError(str(exc))
        
    def getNodes(self):
        try:
            db = self.cnx['local']
            node = db.system.replset.find_one()
            if node is None:
                raise DBError("No node found!")
            return node

        except Exception as exc:
            raise DBError(str(exc))
        
    def addNode(self, server_node, is_arbiter=False, is_hidden=False, priority=1, votes=1):
        '''
            arbiterOnly = false : If true, this member will participate in vote but receive no data.
            votes  = 1: Number of votes this member has in an election. Generally you should not change this
        '''
        nodes = self.getNodes()
        if nodes.has_key('version'):
            # incrase version by 1
            nodes['version'] += 1

        if nodes.has_key('members'):
            total_members = len(nodes['members'])
            node = {'host': server_node, '_id': total_members, 'arbiterOnly': is_arbiter, 'hidden': is_hidden, 'priority': priority, 'votes': votes }
            nodes['members'].append(node)
        try:
            cmd = {DbAdmin.CMD_RECONFIG_REPLICASET : nodes}
            return self._executeCommand(cmd)
        except Exception, exc:
            raise DBError(str(exc))
        
    def getStatusReplicaSet(self):
        '''
            Check replica set status.
            Return state for each replica:
                0     Starting up, phase 1 (parsing configuration)
                1     Primary
                2     Secondary
                3     Recovering (initial syncing, post-rollback, stale members)
                4     Fatal error
                5     Starting up, phase 2 (forking threads)
                6     Unknown state (member has never been reached)
                7     Arbiter
                8     Down
                9     Rollback
                10    Removed            
        '''
        return self._executeCommand(DbAdmin.CMD_REPLICA_SET_STATUS)

    def checkReplicaSetType(self):
        self._executeCommand(DbAdmin.CMD_REPLICA_SET_IS_MASTER)
        
    def showReplicaConfig(self):
        '''
            rs.conf()
        '''
        pass
    
    def showMasterStatus(self):
        ''' 
            Show replication MASTER status
            db.printReplicationInfo() -> inspects contents of local.oplog.$main on master and reports status

        '''
        try:
            db  = self.cnx['local']
            status = {}
            status['master'] = list(db.oplog['$main'].find())
            return status
        except Exception, exc:
            raise DBError(str(exc))
    
    def showSlaveStatus(self):
        ''' 
            Show replication SLAVE status
            db.printSlaveReplicationInfo() -> inspects contents of local.sources on the slave and reports status

        '''
        try:
            db  = self.cnx['local']
            status = {}
            status['whoiam'] = list(db.me.find()) 
            status['slave']  = list(db.sources.find())
            return status
        except Exception,exc:
            raise DBError(str(exc))
    
    def addShardNode(self, server_or_replicaset):
        '''
            Add new shard - thought mongos!
            Equivalent with mongo cmd:
                 > use admin
                 > db.runCommand( { addshard : "set1/server1A,server1B,server1C", name : "shard1" }
                     ... { "shardAdded" : "shard1", "ok" : 1 }
        '''
        cmd = {DbAdmin.CMD_ADD_SHARD : server_or_replicaset}
        return self._executeCommand(cmd)
    
    def removeShard(self, shard_name):
        '''
            Remove a shard from an existing cluster.
            !Note: The balancer must be running for this process to work. 
                   It does all the work of migrating chunks and removing the shard when that is done.
            
        '''
        cmd = {DbAdmin.CMD_REMOVE_SHARD : shard_name }
        return self._executeCommand(cmd)
    
    def shutdownShard(self, shard_name):
        '''
           After the 'removeshard' command reported being done with that shard, you can take that shard down. 
        '''
        self.removeShard(shard_name)
    
    def listDatabases(self):
        '''
            List all databases
        '''
        cmd = {DbAdmin.CMD_LIST_DATABASES : 1 }
        return self._executeCommand(cmd)
    
    def dropDb(self, database):
        '''
            Drop current database
            Result : {JSON} 
                -> {u'ok': 1.0, u'dropped': u'gogo'}
        '''
        if not isinstance(database, basestring):
            raise TypeError("database must be an instance of (Database, str, unicode)")

        db  = self.cnx[database]
        return db.command(DbAdmin.CMD_DROP_DATABASE)
    
    def moveToPrimary(self, db, shard_name):
        '''
            MovePrimary should only be run after the shard has finished draining (i.e. all chunks have been removed, the status may not update),
            and only for those databases with primaries on the drained shard.
            
            Important: You should only issue the movePrimary command after draining has completed - in general you should never use movePrimary
                       if you still have undrained sharded collection data on the primary shard.
      
            Example:
                    shard = Shard(**args)
                    shard.moveToPrimary("hat","172.16.101.229:27021")
                        -> response: {u'ok': 1.0, u'primary ': u'shard0001:172.16.101.229:27021'}
                        -> in mongos console:
                                Thu Mar 15 17:19:05 [conn7] distributed lock 'hat-movePrimary/L-MOB-COSTIA:27017:1331824364:41' acquired, ts : 4f6208693b5dcce9c98c24a3
                                Thu Mar 15 17:19:05 [conn7] movePrimary:  dropping hat from old
                                Thu Mar 15 17:19:05 [conn7] distributed lock 'hat-movePrimary/L-MOB-COSTIA:27017:1331824364:41' unlocked.
        '''
        cmd = SON(
                  [
                    (DbAdmin.CMD_MOVE_PRIMARY,db),
                    (DbAdmin.CMD_TO, shard_name)
                   ]
                  )        
        return self._executeCommand(cmd)
    
    def copyTo(self, from_db, to_db, from_host):
        database._check_name(to_db)
        cmd = SON(
                  [
                    (DbAdmin.CMD_COPY_DB, 1),
                    (DbAdmin.FROM_HOST, from_host),
                    (DbAdmin.FROM_DB, from_db),
                    (DbAdmin.TO_DB, to_db)
                   ]
                  )
        return self._executeCommand(cmd)
    
    def enableShardingOnDB(self, db):
        '''
            Enable sharding for DB = throught router (mongo) 
            Example:
                admin.enableShardingOnDB("test")
        '''
        return self._executeCommand({DbAdmin.CMD_ENABLE_SHARDING : db})
    
    def shardCollection(self, collection_name, shard_key, unique=False):
        '''
            Shard collection
            Example:
                admin.shardCollection("test.foo.empathy",{empathyse: 1})
                
            Note:
                You can use the {unique: true} option to ensure that the underlying index enforces uniqueness
                so long as the unique index is a prefix of the shard key. (note: prior to version 2.0 this worked only if the collection is empty).
            
            Choosing a shard key: http://www.mongodb.org/display/DOCS/Choosing+a+Shard+Key            
        '''
        key = {shard_key:1}
        cmd = SON(
                  [
                    (DbAdmin.CMD_SHARD_COLLECTION, collection_name),
                    ('key', key)
                  ]
                  )
        return self._executeCommand(cmd)
        
    
    def listShards(self):
        '''
            List all shards
        '''
        return self._executeCommand({DbAdmin.CMD_LIST_SHARDS : 1})

    def shardStatus(self):
        '''
            Print sharding status - runt this throught mongos
        '''
        try:
            db  = self.cnx['config']
            status = {}
            status['version'] = self._router_ver(db)
            # extract from "shards"
            status['shards'] = self._get_shards(db)
            # extract from "databases"
            status['databases'] = self._db_list(db)            
            return status
        except Exception, exc:
            raise DBError(str(exc))
    
    def routerStatus(self):
        '''
            Show router status
        '''        
        try:
            db  = self.cnx['config']
            status = {}
            status['version'] = self._router_ver(db)
            status['locks'] = self._router_locks(db)
            status['pings'] = self._router_lockpings(db)
            status['routers'] = self._routers(db)
            return status
        except Exception, exc:
            raise DBError(str(exc))
    
    def getIndexes(self, database):
        '''
             View database indexes
             return JSON object:
                 [{
                     'ns': 'test.hat', 'name': '_id_', 'key': {u'_id': 1}, 'v': 1
                  },{
                     'ns': 'test.hata','name': '_id_', 'key': {u'_id': 1}, 'v': 1
                  },{
                     'ns': 'test.hat','name': 'myindex', 'background': False, 'dropDups': False, 'key': {'aaaa': 1}, 'v': 1, 'unique': True
                  }]
        '''
        try:
            db = self.cnx[database]
            index_list = db.system.indexes.find()
            if index_list.count() == 0:
                raise DBError("No index defined!")
            return list(index_list)
        except Exception, exc:
            raise DBError(str(exc))
     
    def dropIndex(self, collection, index_name):
        '''
            CMD_DELETE_INDEX
        '''
        if collection.find(DOT) == -1:
            raise DBError("Database or collections not specified. Use addIndex(<db.colection>,...) ")
        res = collection.split(DOT)
        try:
            database = res[0]
            col = res[1]
            db = self.cnx[database]
            
            cmd = SON(
                 [
                    (DbAdmin.CMD_DROP_INDEX,col),
                    ('index', index_name)
                  ]
                  )     
            db.command(cmd)       
            return list(self.getIndexes(database))
        except Exception as exc:
            raise DBError(str(exc))
    
    def dropIndexes(self,collection):
        return self.dropIndex(collection, ASTERISK)
        
    def addIndex(self, collection, index_name, index_key, unique=False, drop_duplicates=False, create_in_background=False, index_version=1):
        '''
            Example:
                mongo.addIndex('test.hat','_idx_hat',{'name':1},unique=True,drop_duplicates=True,create_in_backgroud=True,index_version=2)
        
        
            unique - MongoDB indexes may optionally impose a unique key constraint, 
                     which guarantees that no documents are inserted whose values for the indexed keys match
                     those of an existing document.
            drop_duplicates - A unique index cannot be created on a key that has pre-existing duplicate values.
                     If you would like to create the index anyway, keeping the first document the database indexes and 
                     deleting all subsequent documents that have duplicate values, add the dropDups option.
            create_in_backgroud - v1.4+ has a background index build option.This option has significant limitations in a replicated cluster
            index_version - index version = 1 in v2.0
                     
            More details at: http://www.mongodb.org/display/DOCS/Indexes
            
        '''
        if collection.find(DOT) == -1:
            raise DBError("Database or collections not specified. Use addIndex(<db.colection>,...) ")
        if not isinstance(index_key, dict):
            raise DBError("Index key not instance of dict!")
        res = collection.split(DOT)
        try:
            database = res[0]
            col_name = res[1]
            db = self.cnx[database]
            col_indexes = db.system.indexes
            idx_obj = {
                       'name':index_name,
                       'ns': collection,
                       'key': index_key,
                       'background': create_in_background,
                       'dropDups': drop_duplicates,
                       'unique':unique,
                       'v': index_version
                       }
            col_indexes.insert(idx_obj,safe=True)
            return list(self.getIndexes(database))
        except Exception as exc:
            raise DBError(str(exc))
     
    def _db_list(self, db):
        # extract from "databases"            
        return list(db.databases.find())
    
    def _routers(self, db):
        return list(db.mongos.find())
        
    def _router_ver(self, db):
        version = db.version.find_one()
        if version is None:
            raise DBError("Not a shard database!")
        return version
    
    def _router_locks(self, db):
        return list(db.locks.find())
    
    def _router_lockpings(self, db):
        return list(db.lockpings.find())
    
    def _get_shards(self, db):
        shards = db.shards.find()
        if shards.count() == 0:
            raise DBError("No shards defined!")
        srv_shards = []
        for shard in shards:
            srv_shards.append({'_id' : shard['_id'], 'host' : shard['host']})
        return srv_shards