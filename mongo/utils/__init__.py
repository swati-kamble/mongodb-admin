'''
Created on Mar 5, 2012

@author: Adrian Costia
'''

import imp
import platform
from socket import error, socket, AF_INET, SOCK_STREAM,SOCK_DGRAM, inet_ntoa,gethostname
from optparse import OptionParser
from subprocess import Popen, PIPE, STDOUT
import struct

fcntl_module_exists = False
fcntl_module = None
if 'Linux' in platform.system():
    module = "fcntl"
    # check for module
    fp, pathname, description = imp.find_module(module)
    try:
        # try to load "fcntl" module
        fcntl_module = imp.load_module(module, fp, pathname, description)
        fcntl_module_exists = True
    finally:
        if fp:
            fp.close()
   
class Network:
    def __init__(self):
        self.hostname = None
        self.domain   = None

    def getHostName(self):
        proc   = Popen(['hostname','-A'], stdout=PIPE, stderr=PIPE)
        result = proc.wait()
        if result == 0:
            self.hostname = proc.stdout.read()
        return self.hostname

    def getDomain(self):
        proc   = Popen(['hostname','-d'], stdout=PIPE, stderr=PIPE)
        result = proc.wait()
        if result == 0:
            self.domain = proc.stdout.read()
        return self.domain

    def getHostByDomain(self):
        host = str(self.getHostName())
        if len(host) == 0:
            host = str(self.getHostName()) + "."+ str(self.getDomain())
        return host

    def getHost(self):
        self.hostname = gethostname()
        return self.hostname

    def getIpAddress(self, iface): # getIpAddress('eth0')
        if platform.system == "Linux" and fcntl_module_exists == True:
            s = socket(AF_INET, SOCK_DGRAM)
            ipAddr  =  inet_ntoa(fcntl_module.ioctl(s.fileno(), 0x8915, struct.pack('256s', iface[:15]))[20:24])
            return str(ipAddr)
        else:   # on windows
            ipAddr = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1]
            return str(ipAddr)

    def getHwAddr(self,ifname=None):   # getHWAddr('eth0')
        if 'Linux' in platform.system() and fcntl_module_exists == True:
            if ifname == None:
                raise Exception('eth not specified!')
            s = socket(AF_INET, SOCK_DGRAM)
            info = fcntl_module.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
            hwaddr = ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]
            return str(hwaddr)
        else:
            '''
                http://docs.python.org/library/uuid.html
                uuid.getnode() :
                    Get the hardware address as a 48-bit positive integer. The first time this runs,
                    it may launch a separate program, which could be quite slow. 
                    If all attempts to obtain the hardware address fail, we choose a random 48-bit number 
                    with its eighth bit set to 1 as recommended in RFC 4122.
                    "Hardware address" means the MAC address of a network interface,
                    and on a machine with multiple network interfaces the MAC address of 
                    any one of them may be returned. 
            '''
            import uuid
            mac_address = str(hex(uuid.getnode()))
            hwaddr = mac_address.replace("0x", "").replace("L", "").upper()
        return str(hwaddr)

# test
if __name__ == "__main__":
    net = Network()
    mac = net.getHwAddr('eth0')
    print mac
