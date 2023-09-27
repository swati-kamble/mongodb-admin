#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 encoding=utf-8

# Copyright (C) 2012 Costia Adrian
# Created on Mar 5, 2012
#   -updated on Decc 06, 2012
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

import random
import sys
from mongo.utils.const import *
from mongo.utils.util  import *
from operations import *
from optparse import OptionParser, OptParseError


class MongoUtil:

    def examples(self,options,args):
        print "Usage: %s start|stop|config|shard|router|replicaset|master|slave|<options>" % sys.argv[0]
        print 
        print "  EXAMPLES : "
        print "     server 1 : alpha - IP address 10.179.65.220 "
        print "     server 2 : beta  - IP address 10.179.65.221 "
        print "     server 3 : gama  - IP address 10.179.65.223 "
        print "     server 4 : delta - IP address 10.179.65.224 "
        print 
        print "    -- SHARDING 3 SERVERS WITH REPLICA SET: "
        print "          -- run servers: "
        print "              -- on alpha : mongo-admin --shard /data/db/shard/s1/ --replica csign/10.179.65.221:27020 --port 27020 --bind 10.179.65.220 --logpath /var/log/mongodb/mongodb.log"
        print "              -- on beta  : mongo-admin --shard /data/db/shard/s2/ --replica csign/10.179.65.222:27020 --port 27020 --bind 10.179.65.221 --logpath /var/log/mongodb/mongodb.log"
        print "              -- on gamma : mongo-admin --shard /data/db/shard/s3/ --replica csign/10.179.65.220:27020 --port 27020 --bind 10.179.65.222 --logpath /var/log/mongodb/mongodb.log"
        print "          -- init replica: "
        print "              -- on alpha : mongo-admin --initreplica csign 10.179.65.220:27020,10.179.65.221:27020,10.179.65.222:27020 "
        print "                    -> response: ...Config now saved locally. Should come online in about a minute ..."
        print "          -- run config server:"
        print "              -- on delta : mongo-admin --config /data/db/config/ --port 20000 --bind 10.179.65.224 --logpath /var/log/mongodb/mongodb.log"
        print "          -- run router:"
        print "              -- on delta : mongo-admin --router 10.179.65.220:20000 --port 27021 --bind 10.179.65.224 --logpath /var/log/mongodb/mongodb.log"
        print "          -- create the shard:"
        print "              -- on delta : mongo-admin --addshard csign/10.179.65.220:27020,10.179.65.221:27020,10.179.65.222:27020"
        print "              -- on delta : mongo-admin --listshards"                
        print "          -- enable sharding for database:"
        print "              -- on delta : mongo-admin --enablesharding test "
        print "          -- enable sharding for collection using a key:"        
        print "              -- on delta : mongo-admin --shardcollection test.cars manufacturer "
        print "                             -> where: test.cars = db.collection ; manufacturer = key "
        print 
        print "    -- SIMPLE REPLICATION 2 SERVERS: "
        print "          -- run master: "
        print "              -- on alpha : mongo-admin --master /data/db/master/ --port 27022 --bind 10.179.65.220 --logpath /var/log/mongodb/mongodb.log"
        print "          -- run slave: "
        print "              -- on beta  : mongo-admin --slave /data/db/slave/ --source 10.179.65.220:27022 --port 27022 --bind 10.179.65.221 --logpath /var/log/mongodb/mongodb.log"
        print 
        print "    -- REPLICASET 3 SERVERS: "
        print "          -- run server 1: "
        print "              -- on alpha : mongo-admin --replicaset repl01 --dbpath /data/db/replica/ --port 27020 --bind 10.179.65.220 --logpath /var/log/mongodb/mongodb.log" 
        print "          -- run server 2: "
        print "              -- on beta  : mongo-admin --replicaset repl01 --dbpath /data/db/replica/ --port 27020 --bind 10.179.65.221 --logpath /var/log/mongodb/mongodb.log"
        print "          -- run server 3: "
        print "              -- on gamma : mongo-admin --replicaset repl01 --dbpath /data/db/replica/ --port 27020 --bind 10.179.65.223 --logpath /var/log/mongodb/mongodb.log"
        print "          -- init replicaset: "
        print "              -- on beta : mongo-admin --initreplica repl01 10.179.65.220:27020,10.179.65.221:27020,10.179.65.222:27020"
        print
        print "    -- SERVER STATUS: "
        print "          -- server info: mongo-admin --serverinfo --bind 10.179.65.220 --port 27022"
        print "                    -> response: {JSON} -> ...{flushes': 29, 'average_ms': 27.06896551724138, 'total_ms': 785} ... "
        print "          -- replica set: mongo-admin --replicastatus --bind 10.179.65.224 --port 27022"
        print "                    -> response: {JSON}"
        print "          -- replication master : mongo-admin --masterinfo --bind 10.179.65.220 --port 20037 "
        print "                    -> response: {JSON}"
        print "          -- replication slave : mongo-admin --slaveinfo --bind 10.179.65.221 --port 27022 "
        print "                    -> response: {JSON}"
        print "          -- shard  : mongo-admin --shardstatus --bind 10.179.65.224 --port 27021 "
        print "                    -> response: {JSON}"
        print "          -- router : mongo-admin --routerstatus --bind 10.179.65.224 --port 27021"
        print "                    -> response: {JSON}"
        print
        print "    -- IS MASTER ? "
        print "          -- on beta : mongo-admin --ismaster"
        print "                    -> response: {JSON}"
        print "    -- OPERATIONS  "
        print "          -- list database indexes     : mongo-admin --listindexes test"
        print "          -- add index                 : mongo-admin --addindex collection=gogo.mumu name=idx_name key={'prenume':1} unique=True drop_duplicates=False"
        print "                                       : mongo-admin --addindex test.hat idx_name {'name':1} True False"
        print "          -- drop index                : mongo-admin --dropindex test.hat idx_name"
        print "                                       : mongo-admin --dropindex collection=test.hat index=idx_name"
        print "                                       : mongo-admin --dropindex collection=test.hat *"
        print "          -- move database to server   : mongo-admin --moveto test alpha"
        print "                    -> where 'test' is database and 'alpha' is the server"
        print "          -- copy database to server   : mongo-admin --copyto hat hats localhost:27018"
        print "          -- list databases            : mongo-admin --listdb "        
        print "          -- drop database from server : mongo-admin --dropdb hat --bind 10.179.65.221 --port 27022"
        print "          -- add user                  : mongo-admin --adduser test superuser superpass"
        print "          -- delete user               : mongo-admin --deluser test superuser"
        print "          -- check data integrity      : mongo-admin --validate test.hat"        
        print "          -- repair database           : mongo-admin --repair test"
        print "          -- compact/defragments coll  : mongo-admin --compact test.hat"
        print "          -- view server log           : mongo-admin --serverlog"
        print "          -- view server info          : mongo-admin --serverinfo"
        print "          -- view current operations   : mongo-admin --currentops"
                    
    def start(self, options, args):
        mongo.start(bind_ip=options.bind, port=options.port, logpath=options.logpath, key=options.key, demonize=options.demonize, rest=options.webadmin)
    def stop(self):
        mongo.stop()

    def shard(self,options,args):
        '''
            Example:
                Simple sharding:
                    mongo-admin --shard /data/db/shard/s1/ --replica csign/172.16.101.229:27020 --port 27020 --bind 172.16.101.229 --logpath mongodb.log                
                
                Sharding with replicaSet (failover)
        '''
        
        if options.shard is None:
            print "Database path not specified. Example: mongo-admin --shard /data/db/shard/s1/ "
            sys.exit(2)
        
        if options.replica is not None:
            use_replica = True
            servers     = options.replica
        else: 
            use_replica = False
            servers     = None
        # start shard    
        mongo.startShard(db_path=options.shard, use_replica=use_replica, servers=servers, bind_ip=options.bind, port=options.port, logpath=options.logpath, key=options.key)

    def config(self, options, args):
        '''
            Example:
                mongo-admin --config /data/db/config/ --port 20000 --bind 172.16.101.229 --logpath mongodb.log
        '''
        if options.config is None:
            print "Database path not specified. Example: mongo-admin --config /data/db/config/"
            sys.exit(2)
        # start config server
        mongo.startConfigServer(db_path=options.config, bind_ip=options.bind, port=options.port, logpath=options.logpath, key=options.key)

    def router(self, options, args):
        '''
            Example:
                mongo-admin --router 10.179.65.220:20000 --logpath /var/log/mongodb/mongodb.log --port 27021 --bind 10.179.65.220
        '''
        if options.router is None:
            print "Router address invalid!"
            sys.exit(2)
    
        # check hosts
        servers_list = parse_hosts(options.router)
    
        # execute router
        mongo.startRouter(servers=servers_list, port=options.port, bind_ip=options.bind, logpath=options.logpath, key=options.key)

    def replicaset(self, options, args):
        
        if options.replicaset is None:
            print "Replica name must be specified. Example: mongo-admin --replicaset csign "
            sys.exit(2)
        if options.dbpath is None:
            print "Database path not specified. Example: mongo-admin --replicaset csign --dbpath /data/replica/r0"
            sys.exit(2)
        # run replica set
        mongo.startReplicaSet(name=options.replicaset, db_path=options.dbpath, port=options.port, bind_ip=options.bind, logpath=options.logpath, key=options.key)
    
    def master(self,options,args):
        '''
            Start replica - master 
            
            Example:
               mongo-admin --master /data/db/master/ --bind 172.16.101.229 --port 20002
        '''
        if options.master is None:
            print "MASTER Database path not specified. Example: mongo-admin --master /data/db/master/ "
            sys.exit(2)
        mongo.startMaster(db_path=options.master, port=options.port, bind_ip=options.bind, logpath=options.logpath, key=options.key)
        
    def slave(self, options, args):
        '''
            Start replica - slave 
            
            Example:
               mongo-admin --slave /data/db/slave/ --source 172.16.101.229:20002 --bind 172.16.101.229 --port 20002
        '''
        if options.slave is None:
            print "SLAVE Database path not specified. Example: mongo-admin --slave /data/db/slave/ "
            sys.exit(2)
        if options.source is None:
            print "MASTER host must be specified. Example: --slave /data/db/slave/ --source 172.16.101.229:20003 --bind 172.16.101.229 --port 20002"
        # check master
        parse_hosts(options.source)
        mongo.startSlave(master=options.source, db_path=options.slave, port=options.port, bind_ip=options.bind, logpath=options.logpath, key=options.key)

    def initreplica(self, options, args):
        '''
            Init replica set
            Example: mongo-admin --initreplica csign 172.16.101.229:27017,172.16.101.229:27018
                
        '''
        if options.initreplica is None:
            print "Replica name/servers are not specified in the request."
            sys.exit(2)

        replica_name = options.initreplica[0]
        srv_list     = options.initreplica[1]
        
        servers = parse_hosts(srv_list)
        config = {}
        config["_id"] =  replica_name
        members       =  []
        
        # start config
        cnt      = 0
        for server in servers:
            priority = random.randrange(0, 2)
            if cnt == 0:
                priority = 1
            else:
                priority = random.randrange(0,2)
            members.append({"_id" : cnt, "host": server, "priority" : priority })
            cnt += 1
        config['members'] = members
        # initiate replica
        initiate = mongo.initiateReplicaSet(config=config, port=options.port, bind_ip=options.bind)

    def replicastatus(self, options, args):
        '''
            Show replica set status
                Example: mongo-admin --replicastatus --bind 172.16.101.229 --port 20002
        '''
        print mongo.statusReplicaSet(port=options.port, bind_ip=options.bind)
        
    def ismaster(self, options, args):
        '''
            Check to see if server is master
                Examle: mongo-admin --ismaster
        '''
        print mongo.isMaster(port=options.port, bind_ip=options.bind)
        
    def addnode(self, options, args):
        '''
            Add new replica node
             Example:   mongo-admin --addnode 172.16.101.229:27019
        '''
        parse_hosts(options.addnode)
        return mongo.addNode(host=options.addnode, port=options.port, bind_ip=options.bind)

    def listnodes(self, options, args):
         '''
             List all replica nodes
                 Example: mongo-admin --listnodes
         '''
         print mongo.listNodes(port=options.port, bind_ip=options.bind)

    def addshard(self, options, args):
        '''
            Add new shards
               Example: mongo-admin --addshard 192.168.176.128:27020 --port 30000 , where 30000 is mongos router port
        '''
        if options.addshard is None:
            print "Please specify the shard server. The sintax is: mongo-admin <server_name_or_replica_servers:port> "
            sys.exit(2)
        srv_list   = options.addshard
        print mongo.addShardNode(servers=srv_list, port=options.port, bind_ip=options.bind)
    
    def listshards(self, options, args):
        '''
            List all shards
                Example: mongo-admin --listshards 
        '''
        print mongo.listShards(port=options.port, bind_ip=options.bind)
    
    def enablesharding(self, options, args):
        '''
            Enable shard for database 
                Example: mongo-admin --enablesharding test --port 30000, where 30000 is the mongos router port
        '''
        if options.enablesharding is None:
            print "Database is not specified!"
            sys.exit(2)
        print mongo.shardDB(options.enablesharding, port=options.port, bind_ip=options.bind)
        
    def shardcollection(self, options, args):
        '''
            Enable sharding for a collection
                Sintax: mongo-admin --shardcollection <db.collection_name> <key_name> --port=<router_port> --bind=<router_address>
                Example: mongo-admin --shardcollection hat.brown name --port 30000, where 30000 is the mongos router port
        '''
        if options.shardcollection is None:
            print "Collection name is not specified!"
            sys.exit(2)

        collection  = options.shardcollection[0]
        key         = options.shardcollection[1]
        print mongo.shardCollection(collection, key, port=options.port, bind_ip=options.bind)
        
    def shardstatus(self, options, args):
         '''
             Show shards status - available only through  mongo router
                 Example: mongo-admin --shardstatus --bind=192.168.0.23 --port 30000 , where "30000" is the mongos router port
         '''
         print mongo.statusShards(port=options.port, bind_ip=options.bind)
    
    def serverinfo(self, options, args):
        '''
            Show server info
                Example: mongo-admin --serverinfo
        '''
        print mongo.serverInfo(port=options.port, bind_ip=options.bind)
   
    def serverlog(self, options, args):
        '''
            View server log
                Example: mongo-admin --serverlog
        '''
        print mongo.serverLog(port=options.port, bind_ip=options.bind)
    
    def currentops(self, options, args):
        '''
            View current operations
                Example: mongo-admin --currentops
        '''  
        print mongo.viewOperations(port=options.port, bind_ip=options.bind)
        
    def repair(self, options, args):
        '''
            Repair database
                Example: mongo-admin --repair hat, where "hat" is the database
        ''' 
        print mongo.repair(options.repair, port=options.port, bind_ip=options.bind)
    
    def compact(self, options, args):
        '''
            The compact command compacts and defragments a collection.
                Example: mongo-admin --compact test.hat
        '''
        print mongo.compactCollection(options.compact, port=options.port, bind_ip=options.bind)
    
    def validate(self, options, args):
        '''
            Check data integrity
                Example: mongo-admin --validate hat.hats, where "hat" is database and "hats" is the collection
        '''
        print mongo.checkDataIntegrity(options.validate, port=options.port, bind_ip=options.bind)
      
    def masterinfo(self, options, args):
        '''
            Show master info
                Example: mongo-admin --masterinfo --bind=192.168.0.23 --port 30000
        '''
        print mongo.masterStatus(port=options.port, bind_ip=options.bind)
    
    def slaveinfo(self, options, args):
        '''
            Show slave info
                Example: mongo-admin --slaveinfo --bind=192.168.0.23 --port 30000
        '''
        print mongo.slaveStatus(port=options.port, bind_ip=options.bind)
    
    def routerstatus(self, options, args):
        '''
            Show router (mongos) status
                Example : mongo-admin --routerstatus --bind=192.168.0.23 --port 30000 , where "30000" is the mongos router port
        '''
        print mongo.statusRouter(port=options.port, bind_ip=options.bind)

    def moveto(self, options, args):
        '''
            Move database to...
                Example: To move db "test" on shard002: mongo-admin --moveto test shard002
        '''
        print mongo.moveTo(options.moveto[0], options.moveto[1], port=options.port, bind_ip=options.bind)
    
    def copyto(self, options, args):
        '''
            Copy database to...
                Example: Copy database "hats" to "hat" to server <x> : mongo-admin --copyto hats hat 192.168.0.123 
        '''
        print mongo.copyTo(options.copyto[0], options.copyto[1], options.copyto[2], port=options.port, bind_ip=options.bind)
    
    def addindex(self, options, args):
        '''
            Add index:
                Example:    - mongo-admin --addindex collection=gogo.mumu name=idx_name key={'prenume':1} unique=True drop_duplicates=False"
                            - mongo-admin --addindex test.hat idx_name {'name':1} True False"                
        '''
        collection = getParamValue(options.addindex[0], "collection")
        idx_name   = getParamValue(options.addindex[1], "name")
        idx_key    = eval(getParamValue(options.addindex[2], "key"))
        try:
            is_unique   = to_bool(getParamValue(options.addindex[3], "unique"))
        except IndexError:
            is_unique   = False
        try: 
            drop_dups   = to_bool(getParamValue(options.addindex[4], "drop_duplicates"))
        except IndexError:
            drop_dups   = False
        
        print mongo.addIndex(collection,
                             idx_name,
                             idx_key,
                             is_unique,
                             drop_dups,
                             port=options.port,
                             bind_ip=options.bind
                            )
    
    def listindexes(self, options, args):
        '''
            List database indexes
                Examples: mongo-admin --listindexes test
        '''
        print mongo.getIndexes(options.listindexes, port=options.port, bind_ip=options.bind)
    
    def dropindex(self, options, args):
        '''
            Drop index
                Example: 
                    1. mongo-admin --dropindex gogo.mumu idx_name
                    2. mongo-admin --dropindex collection=gogo.mumu index=idx_name
        '''
        try:
            collection = getParamValue(options.dropindex[0], "collection")
        except IndexError:
            collection = options.dropindex[0]
        try:
            idx_name   = getParamValue(options.dropindex[1], "index")
        except IndexError:
            idx_name = options.dropindex[1]
        print mongo.dropIndex(collection, idx_name, port=options.port, bind_ip=options.bind)
    
    def adduser(self, options, args):
        '''
            Add new user
                Examples: mongo-admin --adduser hat acostia m0n3o 
                    - where "hat" is the database, "acostia" is the user and "m0n3o" is the password
        '''
        if options.adduser is None:
            sys.exit(2)

        db   = options.adduser[0]
        user = options.adduser[1]
        pwd  = options.adduser[2]
        mongo.addUser(db, user, pwd)
    
    def deluser(self, options, args):
        '''
            Remove user
                Example: mongo-admin --deluser hat acostia
                    -where "hat" is the database and "acostia" is the username
        '''
        if options.deluser is None:
            sys.exit(2)
        db   = options.deluser[0]
        user = options.deluser[1]
        mongo.delUser(db, user)
    
    def listdb(self, options, args):
        '''
            List dababases
                Example: mongo-admin --listdb
        '''
        print mongo.listDb(port=options.port, bind_ip=options.bind)
    
    def dropdb(self, options, args):
        '''
            Drop database
                Example: mongo-admin --dropdb hat 
        '''
        if options.dropdb is None:
            print "Database name is not specified!"
            sys.exit(2)
        print mongo.dropDb(options.dropdb, port=options.port, bind_ip=options.bind)
        
        
        
optParser       = OptionParser()
mongo           = Mongo()
mongo_util      = MongoUtil()
# get all method from clazz
clazz_methods   = inspect_clazz(mongo_util)


def idx_callback(option, opt_str, value, parser):
    args=[]
    for arg in parser.rargs:
        if arg[0] != "-":
            args.append(arg)
        else:
            del parser.rargs[:len(args)]
            break
    if getattr(parser.values, option.dest):
        args.extend(getattr(parser.values, option.dest))
    setattr(parser.values, option.dest, args)    

def main():
    action_methods = {'examples','start','stop','shard','config','router','replicaset','master','slave','routerstatus',
                      'initreplica','addnode','getnodes','ismaster','replicastatus','addshard','enablesharding','shardcollection',
                      'listshards','shardstatus','masterstatus','slaveinfo','serverinfo','currentops','repair','compact','validate','listdb','moveto','copyto','adduser','deluser',
                      'dropdb','addindex','dropindex','listindexes','serverlog'}

    usage = "Sintax: %prog [options] arg"
    optParser.add_option(
       "--examples", nargs=0, dest="examples", help="Examples"
    )
    optParser.add_option(
        "--start", nargs=0, dest="start", help="Start Mongo DB server - normal mode"
    )
    optParser.add_option(
        "--stop", nargs=0, dest="stop", help="Stop all Mongo instances"
    )
    optParser.add_option(
        "--shard", dest="shard", help="Start Mongo DB shard server. Example: mongo-admin --shard /data/db/shard/s1/ "
    )
    optParser.add_option(
        "--replica", help="Specify shard replicaSet. This option works with --shard. Example: mongo-admin --shard /data/db/shard/s1/ --replica csign/173.16.43.123:27020 --port 27020 --bind 173.16.43.123 --logpath mongodb.log "        
    )
    optParser.add_option(
        "--config", dest="config", help="Start Mongo DB config server. Use comma between servers. Example: mongo-admin --config /data/db/config/ --port 20000 --bind 173.16.43.123 --logpath mongodb.log "
    )
    optParser.add_option(
        "--router", dest="router", help="Start Mongo DB router.Use comma between servers. Example: mongo-admin --router 173.16.43.123:20000,173.16.43.123:20001 --logpath /var/log/mongodb/mongodb.log --port 27021 --bind_ip=173.16.43.123 "
    )
    optParser.add_option(
        "--replicaset", dest="replicaset", help="Start Mongo DB replica set"
    )
    optParser.add_option(
        "--master", dest="master", help="Start Mongo DB replication - master. Sintax: mongo-admin --master <db_path> --bind <host> --port <port>"
    )
    optParser.add_option(
        "--slave", dest="slave", help="Start Mongo DB replication - slave. Sintax: mongo-admin --slave <db_path> --source <master_address:port> --bind <host> --port <port>"
    )
    optParser.add_option(
        "--source", help="Set master server in replication mode"
    )
    # params
    optParser.add_option(
       "--demonize", default=True, help="Demonize Mongo DB. Default value : False"
    )
    optParser.add_option(
       "--webadmin", default=True, help="Enable web admin. Default value : False"
    )
    optParser.add_option(
        "--logpath", help="Log to file."
    )
    optParser.add_option(
        "--dbpath", help="DB path"
    )
    optParser.add_option(
        "--port", type=int, default=27017, help="Set mongo port. By default port is 27017. For sharding port is 27018"
    )
    optParser.add_option(
        "--bind", default="127.0.0.1", help="Bind IP. Default: localhost"
    )
    optParser.add_option(
        "--auth", default=False, help="Enable authentication"
    )
    optParser.add_option(
        "--key", nargs=1, help="Enable authentication using a 'key'.A key file must contain at least 6 Base64 characters and be no larger than 1KB (whitespace included). Sintax: mongo-admin --key <path_to_key_file>"
    )
    # admin operation
    optParser.add_option(
        "--repair", nargs=1, dest="repair", help="Repair database. Same as mongod --repair. Sintax: mongo-admin --repair <database> --bind=<server_address> --port=<port>"
    )
    optParser.add_option(
        "--compact", nargs=1, dest="compact", help="Compact collection. Sintax: mongo-admin --compact <database.collection>"
    )
    optParser.add_option(
        "--validate", nargs=1, dest="validate", help="Use the validate command on to check if the contents of a collection are valid. Sintax: mongo-admin --validate <db.collection> --bind=<server_address> --port=<port>"
    )
    optParser.add_option(
        "--serverinfo", nargs=0, dest="serverinfo", help="Get server info. Sintax: mongo-admin --serverinfo --bind=<server_address> --port=<port>"
    )
    optParser.add_option(
        "--serverlog", nargs=0, dest="serverlog", help="View server log. Sintax: mongo-admin --serverlog"
    )
    optParser.add_option(
        "--currentops", nargs=0, dest="currentops", help="View current operations. Sintax: mongo-admin --currentops"
    )
    optParser.add_option(
        "--routerstatus", nargs=0, dest="routerstatus", help="Get router status. Sintax: mongo-admin --routerstatus --bind=<mongo_router_address> --port=<router_port> .Example: mongo-admin --routerstatus --bind=192.168.0.23 --port 30000"
    )
    optParser.add_option(
        "--replicastatus", nargs=0, dest="replicastatus", help="Get replicaSet status. Example: mongo-admin --rstatus"
    )
    optParser.add_option(
        "--masterinfo", nargs=0, dest="masterinfo", help="Get master info. Sintax: mongo-admin --masterstatus --port <master_port>"
    )
    optParser.add_option(
        "--slaveinfo", nargs=0, dest="slaveinfo", help="Get slave info. Sintax: mongo-admin --slaveinfo --port <slave_port>"
    )
    optParser.add_option(
        "--initreplica", nargs=2, dest="initreplica", help="Initiate replica based on config: [mongo-admin --initreplica <replica_name> <server_list> ]  Example: mongo-admin --initreplica set1 173.16.43.123:20000,173.16.43.123:20002"
    )
    optParser.add_option(
        "--addnode", nargs=1, dest="addnode", help="Add new replica node. Example: mongo-admin --addnode 173.16.43.123:20000"
    )
    optParser.add_option(
        "--listnodes", nargs=0, dest="listnodes", help="List replica nodes. Example: mongo-admin --listnodes"
    )
    optParser.add_option(
        "--ismaster", nargs=0, dest="ismaster", help="Check if host is master. Example: mongo-admin --ismaster"
    )
    optParser.add_option(
        "--addshard", dest="addshard", help="Add new shard - through mongos router. Example: mongo-admin --addshard 173.16.43.123:20000 -or- mongo-admin --addshard csign/173.16.43.123:20000,173.16.43.123:20001"
    )
    optParser.add_option(
        "--listshards", nargs=0, dest="listshards", help="List all shards. Example: mongo-admin --listshards"
    )
    optParser.add_option(
        "--shardstatus", nargs=0, dest="shardstatus", help="Get shards status. Sintax: mongo-admin --sstatus --bind=<mongos_router_address> --port=<router_port> .Example: mongo-admin --sstatus --bind=192.168.0.23 --port 30000"
    )
    optParser.add_option(
        "--enablesharding", nargs=1, dest="enablesharding", help="Enable sharding for DB - through mongos router. Example: mongo-admin --enablesharding mydb --port 30000"
    )
    optParser.add_option(
        "--shardcollection", nargs=2, dest="shardcollection", help="Shard a collection - through mongos router. Sintax: mongo-admin --shardcollection <db.collection_name> <key_name> --port=<router_port> Example: mongo-admin --shardcollection hat.brown name --port 30000"
    )
    optParser.add_option(
        "--addindex", action="callback", callback=idx_callback, dest="addindex", help="Add new index on collection. Sintax: mongo-admin --addindex <database.collection> <index_name> <key> <options>"
    )
    optParser.add_option(
        "--dropindex", nargs=2, dest="dropindex", help="Drop (all) index(es) on the specified collection. Use '*' to delete all keys! Sintax: mongo-admin --dropindex <database.collection> <key> "
    )
    optParser.add_option(
        "--listindexes", nargs=1, dest="listindexes", help="Show all indexes available. Sintax: mongo-admin --listindexes <db.colection> "
    )
    optParser.add_option(
        "--moveto", nargs=2, dest="moveto", help="Move database to other server. Sintax: mongo-admin --moveto <database_name> <shard_name>"
    )
    optParser.add_option(
        "--copyto", nargs=3, dest="copyto", help="Move database to other server. Sintax: mongo-admin --copyto <from_db> <to_db> <from_server>"
    )
    optParser.add_option(
        "--listdb", nargs=0, dest="listdb", help="List all databases. Sintax: mongo-admin --listdb"
    )
    optParser.add_option(
        "--dropdb", nargs=1, dest="dropdb", help="Drop database. Sintax: mongo-admin --dropdb <database_name>"
    )
    optParser.add_option(
        "--adduser", nargs=3, dest="adduser", help="Add new user. Sintax: mongo-admin --adduser <database_name> <username> <password>"
    )
    optParser.add_option(
        "--deluser", nargs=2, dest="deluser", help="Delete user. Sintax: mongo-admin --deluser <database_name> <username>"
    )
    
    # parse cmd    
    (options, args) = optParser.parse_args()

    if options.examples: # show examples
        mongo_util.examples()
    else: # search for clazz and execute method
        for option in options.__dict__: 
            if option in action_methods and options.__dict__[option] is not None:
                method = clazz_methods[option]
                # execute clazz method
                ret = method(options,args)

# run main program
if __name__ == '__main__':
    main()
