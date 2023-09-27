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


OPEN_FILE_READ_ONLY  = "r"
OPEN_FILE_WRITE_ONLY = "w"

WIN_DELIMITATOR = "\\"
COMMA           = ","
DOT             = "."
EQUAL           = "="
ASTERISK        = "*"

MONGO_CONF_FILE = "/etc/mongodb.conf"

# define mongo cmd keys
AUTH                = "auth"
NOAUTH              = "noauth"
REST                = "rest"
NOJOURNAL           = "nojournal"
JOURNAL             = "journal"
SMALL_FILES         = "smallfiles"
CPU                 = "cpu"
LOGPATH             = "logpath"
OPLOGGING_LEVEL     = "diaglog" # Set oplogging level where n is 0=off (default) 1=W 2=R 3=both 7=W+some reads
SYNCDELAY           = "syncdelay"   # default 60. seconds between disk syncs. Do not use zero. (more details)
PORT                = "port"
MONGO_BIND_IP       = "bind_ip"
NOHTTP_INTERFACE    = "nohttpinterface"
LOGAPPEND           = "logappend"
SYSLOG              = "syslog"
DB_PATH             = "dbpath"
FORK                = "fork" # running as a daemon in linux
AS_SERVICE          = "install"     # running as a service in windows
NO_UNIX_SOCKET      = "nounixsocket"
NS_SIZE_MB          = "nssize"
NO_HITS             = "nohints"
NO_TABLE_SCAN       = "notablescan"
SECURITY_KEY        = "keyFile"
MAX_CONNECTIONS     = "maxConns"

# replication parameters
MASTER              = "master"
SLAVE               = "slave"
SERVER_SOURCE       = "source"
REPLICATE_ONLY_DB   = "only"
SERVER_ARBITER      = "arbiter"
AUTO_RESYNC         = "autoresync"
SLAVE_DELAY         = "slavedelay"
OPLOG_SIZE          = "oplogSize"
FAST_SYNC           = "fastsync"
REPLICA_SET         = "replSet"
CONFIG_SERVER       = "configsvr"
ROUTER_SERVER       = "configdb"
SHARD_SERVER        = "shardsvr"

# colors xterm
COLOR_RESET   = 0
COLOR_INVERSE = 7
COLOR_CONFIG  =31 #red
COLOR_MONGOS  =32 #green
COLORS_MONGOD =36 #cyan
USE_BOLD_TEXT =True