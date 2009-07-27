#! /usr/bin/env python
# -*- encoding: UTF8 -*-

# author: Philipp Klaus, philipp.l.klaus AT web.de


#   This file is part of netio230a.
#
#   netio230a is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   netio230a is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with netio230a.  If not, see <http://www.gnu.org/licenses/>.



# This class represents the multiple plug hardware Koukaam NET-IO 230A
# It can be configured using raw TCP communication.
# The class aimes at providing complete coverage of the functionality of the box
#  but not every action is supported yet.

# for the raw TCP socket connection:
from socket import *
# for md5 checksum:
import hashlib
# for RegularExpressions:
import re
## for debugging (set debug mark with pdb.set_trace() )
import pdb
# for math.ceil()
import math


class netio230a(object):

    def __init__(self, host, username, password, secureLogin=False):
        self.__host = host
        self.__username = username
        self.__password = password
        self.__secureLogin = secureLogin
        self.__port = 23
        self.__bufsize = 1024
        self.__ports = [ port() , port() , port() , port() ]
        # create a TCP/IP socket
        self.__s = socket(AF_INET, SOCK_STREAM)
        self.__s.settimeout(6)
 
    def login(self):
        # connect to the server
        try:
            self.__s.connect((self.__host, self.__port))
            # wait for the answer
            data = self.__s.recv(self.__bufsize)
        except error:
            errno, errstr = sys.exc_info()[:2]
            if errno == socket.timeout:
                raise NameError("Timeout while connecting to " + self.__host)
                #print "There was a timeout"
            else:
                raise NameError("No connection to endpoint " + self.__host)
                #print "There was some other socket error"
            return False
        # The answer should be in the form     "100 HELLO E675DDA5"
        # where the last eight letters are random hexcode used to hash the password
        if re.search("^100 HELLO [0-9A-F]{8}\r\n$", data) == None:
            raise NameError("Error while connecting: Not received a \"100 HELLO ... signal from the NET-IO 230A")
        if self.__secureLogin:
            m = hashlib.md5()
            data = data.replace("100 HELLO ", "")
            netioHash = data.replace("\r\n", "")
            m.update(self.__username + self.__password + netioHash)
            loginString = "clogin " + self.__username + " " + m.hexdigest() + "\n"
            # log in using the hashed password
            self.__s.send(loginString)
        else:
            # log in however sending the password in cleartext
            self.__s.send("login " + self.__username + " " + self.__password + "\n")
        # wait for the answer
        data = self.__s.recv(self.__bufsize)
        # check the answer for errors
        if re.search("^250 OK\r\n$", data) == None:
            raise NameError("Error while connecting: Login failed; response from NET-IO 230A is:  " + data)

    def getPortStatus(self):
        return self.__sendRequest("port list")
    
    def getFirmwareVersion(self):
        return self.__sendRequest("version")
    
    def getDeviceAlias(self):
        return self.__sendRequest("alias")
    
    def getWatchdogSettings(self,port):
        return self.__sendRequest("port wd " + str(port))
    
    def getNetworkSettings(self):
        return self.__sendRequest("system eth")
    
    def setSwitchDelay(self,seconds):
        return self.__sendRequest("system swdelay " + str(int(math.ceil(seconds*10.0))))
    
    def getSwitchDelay(self):
        return self.__sendRequest("system swdelay")
    
    
    def setPort(self,number,port):
        self.__ports[number] = port
    
    def getPort(self,number):
        self.updatePortsStatus()
        return self.__ports[number]
    
    def updatePortsStatus(self):
        data = self.getPortStatus()
        self.__ports[0].setPortSwitchedOn(bool(int(data[0])))
        self.__ports[1].setPortSwitchedOn(bool(int(data[1])))
        self.__ports[2].setPortSwitchedOn(bool(int(data[2])))
        self.__ports[3].setPortSwitchedOn(bool(int(data[3])))
        #self.__allPorts.getPort1().setPortType()
    
    
    # generic method to send requests to the NET-IO 230A and checking the response
    def __sendRequest(self,request):
        self.__s.send(request+"\n")
        data = self.__s.recv(self.__bufsize)
        if re.search("^250 ", data) == None:
            raise NameError("Error while sending request: " + request + "\nresponse from NET-IO 230A is:  " + data)
            return None
        else:
            return data.replace("250 ","")
    
    def disconnect(self):
	    # close the socket:
        self.__s.close()
    
    def __del__(self):
        self.disconnect()
    ###   end of class netio230a   ----------------



class port(object):

    def __init__(self):
        self.__portType = 0
        self.__powerOn = False
    
    def setPortType(self,portType):
        self.__portType = portType
    
    def setPortSwitchedOn(self,powerStatus):
        self.__powerOn = powerStatus
    
    def getPortSwitchedOn(self):
        return self.__powerOn
    
