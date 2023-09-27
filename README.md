mongodb-admin
=============

An easy way to create a MongoDB cluster

	Author:  Adrian Costia
	Version: 0.0.1

1. How to use MongoDB-Admin (command line )

	-- Servers (example)
	
		-- server 1 : alpha - IP address 10.179.65.220
		-- server 2 : beta  - IP address 10.179.65.221
		-- server 3 : gama  - IP address 10.179.65.223
		-- server 4 : delta - IP address 10.179.65.224
	
	-- SHARDING 3 SERVERS WITH REPLICA SET:
	
		-- run servers:
			on alpha : mongo-admin --shard /data/db/shard/s1/ --replica csign/10.179.65.221:27020 --port 27020 --bind 10.179.65.220 --logpath /var/log/mongodb/mongodb.log
			on beta : mongo-admin --shard /data/db/shard/s2/ --replica csign/10.179.65.222:27020 --port 27020 --bind 10.179.65.221 --logpath /var/log/mongodb/mongodb.log
			on gamma : mongo-admin --shard /data/db/shard/s3/ --replica csign/10.179.65.220:27020 --port 27020 --bind 10.179.65.222 --logpath /var/log/mongodb/mongodb.log
			
		-- init replica:
			on alpha : mongo-admin --initreplica csign 10.179.65.220:27020,10.179.65.221:27020,10.179.65.222:27020
				-> response: ...Config now saved locally. Should come online in about a minute ...
				
		-- run config server:
			on delta : mongo-admin --config /data/db/config/ --port 20000 --bind 10.179.65.224 --logpath /var/log/mongodb/mongodb.log
			
		-- run router:
			on delta : mongo-admin --router --port 27021 --bind 10.179.65.224 --logpath /var/log/mongodb/mongodb.log
			
		-- create the shard:
			on delta : mongo-admin --addshard csign/10.179.65.220:27020,10.179.65.221:27020,10.179.65.222:27020
			on delta : mongo-admin --listshards
			
		-- enable sharding for database:
			on delta : mongo-admin --enablesharding test
			
		-- enable sharding for collection using a key:
			on delta : mongo-admin --shardcollection test.cars manufacturer
				-> where: test.cars = db.collection ; manufacturer = key
				
	-- SIMPLE REPLICATION 2 SERVERS:
	
		-- run master:
			on alpha : mongo-admin --master /data/db/master/ --port 27022 --bind 10.179.65.220 --logpath /var/log/mongodb/mongodb.log
			
		-- run slave:
			on beta : mongo-admin --slave /data/db/slave/ --source 10.179.65.220:27022 --port 27022 --bind 10.179.65.221 --logpath /var/log/mongodb/mongodb.log
	
	
	-- REPLICASET 3 SERVERS:
	
			-- run server 1:
				on alpha : mongo-admin --replicaset repl01 --dbpath /data/db/replica/ --port 27020 --bind 10.179.65.220 --logpath /var/log/mongodb/mongodb.log
				
			-- run server 2:
				on beta : mongo-admin --replicaset repl01 --dbpath /data/db/replica/ --port 27020 --bind 10.179.65.221 --logpath /var/log/mongodb/mongodb.log
				
			-- run server 3:
				on gamma : mongo-admin --replicaset repl01 --dbpath /data/db/replica/ --port 27020 --bind 10.179.65.223 --logpath /var/log/mongodb/mongodb.log
				
			-- init replicaset:
				on beta : mongo-admin --initreplica repl01 10.179.65.220:27020,10.179.65.221:27020,10.179.65.222:2702

	-- SERVER STATUS:
	
			-- server info: mongo-admin --serverinfo --bind 10.179.65.220 --port 27022
				-> response: {JSON} -> ...{flushes': 29, 'average_ms': 27.06896551724138, 'total_ms': 785} ...
				
			-- replica set: mongo-admin --rstatus --bind 10.179.65.224 --port 27022
				-> response: {JSON}
				
			-- replication master : mongo-admin --masterinfo --bind 10.179.65.220 --port 20037			
				-> response: {JSON}
				
			-- replication slave : mongo-admin --slaveinfo --bind 10.179.65.221 --port 27022
				-> response: {JSON}
				
			-- shard : mongo-admin --sstatus --bind 10.179.65.224 --port 27021
				-> response: {JSON}
				
			-- router : mongo-admin --routerstatus --bind 10.179.65.224 --port 27021
				-> response: {JSON}
				
	-- IS MASTER
	
			-- on beta : 
				mongo-admin --ismaster
					-> response: {JSON}
				
	-- OPERATIONS

			list database indexes :
			
					mongo-admin --listindexes test
					
			add index : 
			
					mongo-admin --addindex collection=gogo.mumu name=idx_name key={'prenume':1} unique=True drop_duplicates=False
					mongo-admin --addindex test.hat idx_name {'name':1} True False\
					
			drop index : 
			
					mongo-admin --dropindex test.hat idx_name
					mongo-admin --dropindex collection=test.hat index=idx_name : mongo-admin --dropindex collection=test.hat all (use arterisk)
					
			move database to server :
			
					mongo-admin --moveto test alpha
						-> where 'test' is database and 'alpha' is the server

			copy database to server :
					mongo-admin --copyto hat hats localhost:27018

			list databases :
			
					mongo-admin --listdb
					
			drop database from server :
			
					mongo-admin --dropdb hat --bind 10.179.65.221 --port 27022
					
			add user :
			
					mongo-admin --adduser test superuser superpass
					
			delete user :
			
					mongo-admin --deluser test superuser
					
			check data integrity :
			
					mongo-admin --validate test.hat

			repair database :
			
					mongo-admin --repair test

			compact/defragments coll : 
					mongo-admin --compact test.hat

			view server log :
			
					mongo-admin --serverlog

			view server info :
			
					mongo-admin --serverinfo

			view current operations :
			
					mongo-admin --currentops
					

2. How to configure MongoDB using linux dialogs

	Steps:
	
			1. locate configure-mongodb
			2. chmod +x configure-mongodb
			3. ./configure-mongodb
		
3. Python code example

		Start slave:
		
			from operations import *
			mongo = Mongo()
			mongo.startSlave("192.168.2.100:27020")
			mongo.start()
				-> where 192.168.2.100:27020 = master address
			

		Start replicaSet:
		
			from operations import *
			mongo = Mongo()
			mongo.startReplicaSet(name="csign",db_path="/data/db/replica/r1/",bind_ip="172.16.101.229",port=27020)
		 
		Start config server:
		
			from operations import *
			mongo = Mongo()
			mongo.startConfigServer(db_path="/data/db/replica/r1/",bind_ip="172.16.101.229",port=20000)
		
		Start router:
		
			from operations import *
			mongo = Mongo()
			mongo.startRouter(servers="172.16.101.229:27020",port=27021,bind_ip="172.16.101.229")
		
		Sharding
		
			1. Simple shard:
			
				from operations import *
				mongo = Mongo()
				mongo.startShard(db_path="/data/db/shard/s1/",bind_ip="172.16.101.229",port=20001)
			
			2. With replicaset enabled:
			
				from operations import *
				mongo = Mongo()
				mongo.startShard(
                        db_path="/data/db/shard/s1/",
                        use_replica=True,
                        servers="csing/alpha:27021,beta:27021",
                        bind_ip="172.16.101.229",
                        port=20001
                )
 
		Repair database:
		
			from mongo.admin.mongodb import *
			mongodb = MongoDB(**args)
			mongodb.repair("test")
		
		Copy database to server:
		
			from mongo.admin.mongodb import *
			mongodb = MongoDB(**args)
			mongodb.copyTo("test","my_test","192.168.1.110")
		
		Drop index:
		
			from mongo.admin.mongodb import *
			mongodb = MongoDB(**args)
			mongodb.dropIndex("test.hat","idx_name") 
		
		Shard status:
		
			from mongo.admin.sharding import Shard
			shard = Shard(**args)
			shard.getStatus()
		
		List shards:
		
			from mongo.admin.sharding import Shard
			shard = Shard(**args)
			shard.listShards()
		
		Shard database:
		
			from mongo.admin.sharding import Shard
			shard = Shard(**args)
			shard.shardDb("hat")
		
		Add new node (sharding):
		
			from mongo.admin.sharding import Shard
			shard = Shard(**args)
			shard.addNode("192.168.1.110,192.168.1.111")
		
		Add new replicaSet node:
		
			from mongo.admin.resplicaset import ReplicaSet
			replSet = ReplicaSet(**args)
			replSet.addNode("192.168.1.130")
		
		Initiate replicaSet:
			from mongo.admin.resplicaset import ReplicaSet
			replSet = ReplicaSet(config=config,**args)
			replSet.initiate("192.168.1.130")
		
4.	In development

		1. Mongo-Admin cloud web interface
		2. Mongo-Admin cloud service - manipulate mongo instances via mongo-admin-server (include auto-discovery module)