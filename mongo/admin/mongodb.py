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


import platform
import sys
import atexit
from subprocess import Popen, PIPE, STDOUT
from socket import error, socket, AF_INET, SOCK_STREAM
from select import select
from threading import Thread
from time import sleep
from mongo.utils.const import *
from mongo.utils.util import *
from mongo.utils.procs import *
from mongo.utils.logs import Logger
from mongo.utils.configparser import *
from mongo.utils.exceptions import *
from mongo.admin.dbadm import *


# Find a JSON parser
try:
    import json
    _json = lambda s: json.loads(s)
except ImportError:
    try:
        import simplejson
        _json = lambda s: simplejson.loads(s)
    except ImportError:
        # For Google AppEngine
        from django.utils import simplejson
        _json = lambda s: simplejson.loads(s)

is_windows = (sys.platform == "win32")
is_linux   = (sys.platform == "linux2")

# check MONGO DB config file.
if is_linux:
    if not os.path.isfile(MONGO_CONF_FILE):
        raise FileNotFound("Mongo DB config file not found ")
    
    config = ConfigReader(MONGO_CONF_FILE)
    config.read()
    
    mongo_db_path = config.get("dbpath")
    mongo_log_path= config.get("logpath")
else:
    mongo_log_path= "mongodb.log"
    
# enable logger
logger = Logger("MONGO_ADMIN").log



class MongoParams(object):
    pass

class MongoDB(object):
    """
        Run MongoDB server
    """
    MONGO_LOCATION  = "/usr/bin/"
    if is_linux:    
        MONGOS          = "mongos"
        MONGO_SERVICE   = "mongod"
    elif is_windows:
        MONGOS          = "mongos.exe"
        MONGO_SERVICE   = "mongod.exe"
    MONGO_DB_PATH   = "/data/db/"
    DEFAULT_PORT    = 27017
    BIND_IP         = "127.0.0.1"
    
    def __init__(self, demonize=False, **kwargs):
        '''
            Loaded on init
        '''
        self.params = MongoParams()
        self.demonize(demonize)
        
        self.is_router = False # default use mongod not mongos
        if is_linux:
            self.devnull = open('/dev/null', 'w+')
        else:
            self.devnull = open('nul', 'w+')
            
        self.fds = {}
        self.procs = []
        self.server_command = None
        
        # check files
        if is_linux:
            # get mongo path
            self.mongo_path = os.getenv("MONGO_HOME" , MongoDB.MONGO_LOCATION)
            # set services
            self.mongod = self.mongo_path + MongoDB.MONGO_SERVICE
            self.mongos = self.mongo_path + MongoDB.MONGOS
            # check files
            checkFile(self.mongod)
            checkFile(self.mongos)
            
        elif is_windows:
            
            mongo_path = None
            # search for file mongo.exe
            if not Config.getConfig().has_section("DB"):
                # create new section
                Config.getConfig().add_section("DB")
                            
            try:
                mongo_path = Config.getValue("DB", "path")
            except:
                mongo_path = whereis(MongoDB.MONGO_WINDOWS)
                mongo_path += WIN_DELIMITATOR

                # save to config
                Config.getConfig().set("DB", "path", mongo_path)
                config_file = open(Config._default_web_cfg_file, OPEN_FILE_WRITE_ONLY)
                try:
                    Config.getConfig().write(config_file)
                finally:
                    config_file.close()

            # get mongo path
            self.mongo_path = mongo_path
            
        # set services
        self.mongod = self.mongo_path + MongoDB.MONGO_SERVICE
        self.mongos = self.mongo_path + MongoDB.MONGOS
        
        # set DB path
        if not self.is_router:
            if not hasattr(self.params, DB_PATH):
                if is_windows:
                    self.data_path = MongoDB.MONGO_DB_PATH
                else:
                    self.data_path = mongo_db_path
                # check db "data" folder
                makedirs(self.data_path)
            
        # set DB args
        if kwargs:
            attr2Class(self.params, kwargs)

        # check port
        if not hasattr(self.params, PORT):
            setattr(self.params, PORT, MongoDB.DEFAULT_PORT)
        # check IP
        if not hasattr(self.params, MONGO_BIND_IP):
            setattr(self.params, MONGO_BIND_IP, MongoDB.BIND_IP)
        # check log file
        if not hasattr(self.params, LOGPATH):
            self.setLogFile(mongo_log_path)
       
    def isRouter(self, boolean):
        if not isinstance(boolean, bool):
            raise NotBoolean()
        self.is_router = boolean
        if self.is_router:
            if hasattr(self, "data_path"):
                delattr(self, "data_path")
         
    
    def demonize(self, enabled):
        '''
           Running as a Daemon: --fork (in linux) -or- --install (service in Windows)
           
           Example WIN:
               
               mongod.exe --install --logpath=mongodb.log

           Windows issue:
               Error connecting to the Service Control Manager: Access is denied. (5)
               Wed Mar 07 12:17:44 dbexit: 
               Wed Mar 07 12:17:44 shutdown: going to close listening sockets...
               Wed Mar 07 12:17:44 shutdown: going to flush diaglog...
               Wed Mar 07 12:17:44 shutdown: going to close sockets...
               Wed Mar 07 12:17:44 shutdown: waiting for fs preallocator...
               Wed Mar 07 12:17:44 shutdown: lock for final commit...
               Wed Mar 07 12:17:44 shutdown: final commit...
               Wed Mar 07 12:17:44 shutdown: closing all files...
               Wed Mar 07 12:17:44 closeAllFiles() finished
               Wed Mar 07 12:17:44 dbexit: really exiting now
               
               - resolve issue: 
                   - run mongod.exe as administrator ("Run As Administrator")
                   - start service
               
           Note: these options are only available in MongoDB version 1.1 and later.
           This will fork the Mongo server and redirect its output to a logfile.  
           As with --dbpath, you must create the log path yourself, Mongo will not create parent directories for you.
               
        '''
        if not isinstance(enabled, bool):
            raise NotBoolean()
        if is_linux:
            setattr(self.params, FORK, enabled)
        elif is_windows:
            setattr(self.params, AS_SERVICE, enabled)
        
    
    def enableAuth(self, boolean):
        if to_bool(boolean):
            setattr(self.params, AUTH, True)
        else:
            setattr(self.params, NOAUTH, True)

    def enableWebAdmin(self, boolean):
        '''
            This enables the admin web UI which is useful for viewing the status of the set. 
            It is publicly accessible via HTTP on port 28017 so ensure it is properly firewalled.
        '''
        setParam(self.params, REST, boolean)
                
    def enableJournaling(self, boolean):
        setParam(self.params, JOURNAL, boolean)
    
    def useSmallJournal(self, boolean):
        '''
            Use a smaller initial file size (16MB) and maximum size (512MB)
        '''
        setParam(self.params, SMALL_FILES, boolean)

    def noUnixSocket(self, boolean):
        '''
            Disable listening on unix sockets (will not create socket files at /tmp/mongodb-<port>.sock)
        '''
        setParam(self.params, NO_UNIX_SOCKET, boolean)
    
    def nsSize(self, size_mb):
        '''
            Specifies .ns file size for new databases
        '''
        setattr(self.params, NS_SIZE_MB, size_mb)

    def syncDelay(self, seconds=60):
        '''
            Seconds between disk syncs. Do not use zero.
        '''
        if seconds == 0:
            raise DBError("A 0 setting means never, but is not recommended and should never be used with journaling enabled.")
        setattr(self.params, SYNCDELAY, seconds)
    
    
    def toSysLog(self, boolean):
        '''
            Send all output to syslog. Added in 2.1.0. Not compatible with --logpath
        '''
        setParam(self.params, SYSLOG, boolean)
    
    def setLogFile(self, log_file):
        if not os.path.isfile(log_file):
            try:
                open(self.mongo_path + log_file, OPEN_FILE_WRITE_ONLY).close()            
            except Exception as exc:
                raise Exception("Unable to create LOG file : " + str(exc))
        setattr(self.params, LOGPATH, log_file)
    
    def logAppend(self, boolean):
        '''
            Append to existing log file, instead of overwritting 
        '''
        setParam(self.params, LOGAPPEND, boolean)
    
    def loggingLevel(self, level=0):
        '''
            Set oplogging level where n is:
                -  0=off (default)
                -  1=W 
                -  2=R 
                -  3=both
                -  7=W+some reads
        '''
        setattr(self.params, OPLOGGING_LEVEL, level)
        
    def noHits(self, boolean):
        '''
            Ignore query hints 
        '''
        setParam(self.params, NO_HITS, boolean)
    
    def noTableScan(self, boolean):
        '''
            Turns off table scans. Any query that would do a table scan fails
        '''
        setParam(self.params, NO_TABLE_SCAN,boolean)

    def dbPath(self,path):
        if path is not None:
            if not path_exists(path):
                makedirs(path)
            self.data_path = path
    
    
    def securityKey(self, key):
        '''
            Use security key
            
            A key file must contain at least 6 Base64 characters and be no larger than 1KB (whitespace included).
            On *NIX, group and everyone must have 0 permissions (up to 700 is allowed).
            If the permissions are too open on the key file, MongoDB will exit with an error to that effect.
            
        '''
        setattr(self.params, SECURITY_KEY, key)

    
    def maxConnectionsAllowed(self, max):
        setattr(self.params, MAX_CONNECTIONS, max)
    
    def showCpuUtilization(self, boolean):
        setParam(self.params, CPU, boolean)

    def start(self):
        '''
            Start Mongo server
            
            - Example:
                    mdb = MongoDB(port=29001,objcheck=True,syslog=True,nohints=False,logappend=True)
                    mdb.start()
        '''
        self.runServer()
    
    def stop(self):
        '''
            Stop Mongo server
            
            - Example:
                    mdb = MongoDB(port=29001,objcheck=True,syslog=True,nohints=False,logappend=True)
                    mdb.stop()
        '''
        ps = Process()
        ps.kill_name("mongo")
    
    def suspend(self):
        ps = Process()
        ps.suspend("mongo")
    
    def resume(self):
        ps = Process()
        ps.resume("mongo")
    
    def shutdown(self):
        '''
            Shutdown DB
            
            - Example:
                    mdb = MongoDB(port=29001,objcheck=True,syslog=True,nohints=False,logappend=True)
                    mdb.shutdown()
        '''
        DbAdmin.shutdown()
     
    def serverInfo(self):
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.serverInfo()
        except Exception as exc:
            raise DBError(exc) 
   
    def copyTo(self, from_db, to_db, from_host):
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.copyTo(from_db, to_db, from_host)
        except Exception as exc:
            raise DBError(exc) 
    
    def dropDb(self, db):
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.dropDb(db)
        except Exception as exc:
            raise DBError(exc) 
    
    def addIndex(self, collection, idx_name, idx_key, unique=False, drop_duplicates=False, create_in_background=False, index_version=1):
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.addIndex(collection, idx_name, idx_key, unique, drop_duplicates, create_in_background, index_version)
        except Exception as exc:
            raise DBError(exc) 
        
    def dropIndex(self,collection,index_name):
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.dropIndex(collection, index_name)
        except Exception, exc:
            raise DBError(exc)
    
    def listIndexes(self, collection):
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.getIndexes(database)
        except Exception as exc:
            raise DBError(exc) 

    def listDatabases(self):
        '''
            List all databases
        '''
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.listDatabases()
        except Exception as exc:
            raise DBError(exc) 

    def repair(self, database):
        '''
            Repair database
        '''
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip,port=self.params.port)
            return dbadmin.repairDB(database)
        except Exception as exc:
            raise DBError(exc) 

    def compactCollection(self, collection):
        '''
            Compact collection
        '''
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.compactCollection(collection)
        except Exception as exc:
            raise DBError(exc) 
        

    def checkIntegrity(self, collection):
        '''
            Check data integrity of a collection
        '''
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.checkDataIntegrity(collection)
        except Exception as exc:
            raise DBError(exc)         

    def viewServerLog(self):
        '''
            View server log.
            Return {JSON} :
                {
                    "log" : [
                        "Fri Mar 23 13:56:13 [conn80] build index gogo.mumu { _id: 1 }",
                        "Fri Mar 23 13:56:13 [conn80] build index done 0 records 0.001 secs",
                        "Fri Mar 23 13:56:21 [clientcursormon] mem (MB) res:22 virt:436mapped:160",
                        "Fri Mar 23 13:57:37 [conn59] build index gogo.mumu { nume: 1 }",
                        "Fri Mar 23 13:57:37 [conn59] build index done 3 records 0.002 s
                        ...
                        ...
                    ],
                    "ok" : 1
                }                        
        '''
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.getLog()
        except Exception as exc:
            raise DBError(exc)         

    def viewOperations(self):
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.viewCurrentOperation()
        except Exception as exc:
            raise DBError(exc)         
    
    def initParamaters(self):
        _params = []
        # set default mongo params: mongo server and db path
        mongo_server = self.mongod
        if self.is_router:
            mongo_server = self.mongos
        _params.insert(0, mongo_server)
        # create db_path param
        if hasattr(self, "data_path"):
            db_path = to_param(DB_PATH, self.data_path)
            _params.insert(1, db_path)
        # extract parameters from class
        _params.extend(extract_parameters(self.params))
        self.server_command = _params 
        
    def runServer(self):
        if self.server_command is None:
            raise ServerParametersNotFound()

        print "[Mongo Parameters]" + str(self.server_command)
        # open subprocess and run server
        try:
            process     = Popen(self.server_command, stdin=self.devnull, stdout=PIPE, stderr=STDOUT)
            print "[Mongo DB] Server pid number: " + str(process.pid)
            self.fds[process.stdout] = process
            self.procs.append(process)
            self.pool_process(process)
            sleep(1)
        except Exception as exc:
            raise Exception(str(exc))
    
    def kill(self, process):
        try:
            process.terminate()
        except OSError:
            pass

    def kill_all(self, processes):
        for process in processes:
            try:
                process.terminate()
            except OSError:
                pass

    def pool_process(self, process):
        no_of_trys = 0
        while process.poll() is None and no_of_trys < 20:
            no_of_trys += 1
            s = socket(AF_INET, SOCK_STREAM)
            try:
                try:
                    s.connect((self.params.bind_ip, self.params.port))
                    return
                except (IOError, error):
                    sleep(0.25)
            finally:
                s.close()

        self.kill(process)
        sys.exit(1)
                
    def text_color(self, colorcode): 
        base = '\x1b[%sm'
        if USE_BOLD_TEXT:
            return (base*2) % (1, colorcode)
        else:
            return base % colorcode

    def prefix_color(self, color, text):
        return self.text_color(color) + text + self.text_color(COLOR_RESET)


class ConfigServer(MongoDB):
    '''
        /usr/bin/mongod --configsvr --dbpath=/data/db/config/ --port 20000 --bind_ip=10.179.65.220 --fork --logpath=/var/log/mongodb/mongodb.log
    '''
    def __init__(self, db_path, **kwargs):
        super(ConfigServer, self).__init__(**kwargs)
        # check db path
        if not path_exists(db_path):
            makedirs(db_path)
        # set config db path
        self.data_path = db_path
        # now...is config server 
        setattr(self.params, CONFIG_SERVER, True)
        # init parameters
        self.initParamaters()

class MongoRouter(MongoDB):
    '''
    13205 ?        Sl     7:40 /usr/bin/mongos --configdb 10.179.65.220:20000 --fork --logpath=/var/log/mongodb/mongodb.log

    '''
    def __init__(self,servers=None, **kwargs):
        super(MongoRouter, self).__init__(**kwargs)
        if servers is not None:
            self.isRouter(True)
            # self.data_path = "" # no data for router
            # now...set servers (comma separated)
            setattr(self.params, ROUTER_SERVER, servers)
            # init parameters
            self.initParamaters()
            
    def getStatus(self):
        try:
            dbadmin = DbAdmin(server=self.params.bind_ip, port=self.params.port)
            return dbadmin.routerStatus()
        except Exception as exc:
            raise DBError(exc)     
