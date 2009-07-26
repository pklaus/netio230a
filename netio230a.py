#! /usr/bin/env python
# -*- encoding: UTF8 -*-

# Author: Philipp Klaus, philipp.l.klaus AT web.de


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
# for md5:
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
        # Ein INet Streaming (TCP/IP) Socket erzeugen
        self.__s = socket(AF_INET, SOCK_STREAM)
 
    def login(self):
        # Zum Server verbinden
        self.__s.connect((self.__host, self.__port))
        # Auf Daten vom Server warten
        data = self.__s.recv(self.__bufsize)
        # The answer should be in the form     100 HELLO E675DDA5
        if re.search("^100 HELLO [0-9A-F]{8}\r\n$", data) == None:
            raise NameError("Error while connecting: Not received a 100 HELLO signal from the NET-IO 230A")
        if self.__secureLogin:
            m = hashlib.md5()
            data = data.replace("100 HELLO ", "")
            netioHash = data.replace("\r\n", "")
            m.update(self.__username + self.__password + netioHash)
            loginString = "clogin " + self.__username + " " + m.hexdigest() + "\n"
            self.__s.send(loginString)
        else:
            self.__s.send("login " + self.__username + " " + self.__password + "\n")
        # Auf response vom Server warten
        data = self.__s.recv(self.__bufsize)
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
    
    def __sendRequest(self,request):
        self.__s.send(request+"\n")
        data = self.__s.recv(self.__bufsize)
        if re.search("^250 ", data) == None:
            raise NameError("Error while sending request: " + request + "\nresponse from NET-IO 230A is:  " + data)
            return None
        else:
            #pdb.set_trace()
            return data.replace("250 ","")
    
    def logout(self):
        # Socket schließen
        self.__s.close()

