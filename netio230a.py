#
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



###--------- ToDo next ------------
# http://koukaam.se/koukaam/forum/viewthread.php?forum_id=18&thread_id=399
# Command for enable wd with 360s delay on output 2:
# port wd 2 enable 192.168.10.101 10 360 1 3 enable enable



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
# for shlex.shlex() (to parse answers from the NETIO 230A)
import shlex

import time
### for date.today()
#from datetime import date
from datetime import datetime

class netio230a(object):
    """netio230a is the basic class that you want to instantiate when communicating
    with the Koukaam NETIO 230A. It can handle the raw TCP socket connection and
    helps you send the commands to switch on / off ports etc."""
    
    def __init__(self, host, username, password, secureLogin=False, customPort=23):
        """construct this class by giving:
        
        the host to connect to as a string
        the username as a string
        the password of the NETIO 230A as a string
        secureLogin (bool) if md5 hashed password will be transmitted
        customPort (int) if you changed the port on your NETIO 230A.
        
        Returns an object of class type netio230a.netio230a"""
        self.__host = host
        self.__username = username
        self.__password = password
        self.__secureLogin = secureLogin
        self.__port = customPort
        self.__bufsize = 1024
        self.__ports = [ port() , port() , port() , port() ]
        # create a TCP/IP socket
        self.__s = socket(AF_INET, SOCK_STREAM)
        self.__s.settimeout(6)
        self.__login()
 
    def __login(self):
        """Login to the server using the credentials given to the constructor."""
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
        if re.search("^100 HELLO [0-9A-F]{8}\r\n$", data) == None and re.search("^100 HELLO [0-9A-F]{8} - KSHELL V1.1\r\n$", data) == None  :  # 2nd statement for FW version 2.30
            raise NameError("Error while connecting: Not received a \"100 HELLO ... signal from the NET-IO 230A")
        if self.__secureLogin:
            m = hashlib.md5()
            data = data.replace("100 HELLO ", "")
            data = data.replace(" - KSHELL V1.1", "") # for FW version 2.30
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
        if re.search("^250 OK\r\n$", data) == None :
            raise NameError("Error while connecting: Login failed; response from NET-IO 230A is:  " + data)

    def getPortList(self):
        """Sends request to the NETIO 230A to request the port status.
        
        Returns string specifying which ports are switched on/off.
        For example: "1001" (port 1 and port 4 are on, all others off)"""
        return self.__sendRequest("port list")
    
    def getPortSetup(self,port):
        """Sends request to the NETIO 230A to request the setup of a port given as a parameter.
        
        Returns the status as a string in the format: ..."""
        return self.__sendRequest("port setup " + str(port+1))
    
    def setPortPower(self,port,switchOn=False):
        # the type conversion of switchOn ensures that the values are either "0" or "1":
        self.__sendRequest("port " + str(port) + " " + str(int(bool(int(switchOn)))) )
    
    def setPortTempInterrupt(self,port):
        self.__sendRequest("port " + str(int(port)) + " int" )
    
    def setPortManualMode(self,port,manualMode=True):
        self.__sendRequest("port " + str(int(port)) + " manual")
    
    def getFirmwareVersion(self):
        return self.__sendRequest("version")
    
    def getDeviceAlias(self):
        return self.__sendRequest("alias")
    def setDeviceAlias(self,alias = "netio230a"):
        self.__sendRequest("alias " + alias)
    
    # this command is operation-safe: it does not switch the ports on/off during reboot of the NETIO 230A
    def reboot(self):
        self.__sendRequest("reboot",False)
        self.disconnect()
    
    def getWatchdogSettings(self,port):
        return self.__sendRequest("port wd " + str(port))
    
    def getNetworkSettings(self):
        return self.__sendRequest("system eth")
    def setNetworkSettings(self,dhcpMode=False,deviceIP="192.168.1.2",subnetMask="255.255.255.0",gatewayIP="192.168.1.1"):
        if dhcpMode:
            self.__sendRequest("system eth dhcp")
        else:
            self.__sendRequest("system eth manual " + deviceIP + " " + subnetMask + " " + gatewayIP)
    
    def getDnsServer(self):
        return self.__sendRequest("system dns")
    def setDnsServer(self,dnsServer="192.168.1.1"):
        self.__sendRequest("system dns " + dnsServer)
    
    def getSystemDiscoverableUsingTool(self):
        if self.__sendRequest("system discover") == "enable":
            return True
        else:
            return False
    def setSystemDiscoverableUsingTool(self,setDiscoverable=True):
        if setDiscoverable:
            command = "enable"
        else:
            command = "disable"
        self.__sendRequest("system discover " + command)
    
    def setSwitchDelay(self,seconds):
        return self.__sendRequest("system swdelay " + str(int(math.ceil(seconds*10.0))))
    def getSwitchDelay(self):
        return int(self.__sendRequest("system swdelay"))/10.0
    
    def getSntpSettings(self):
        return self.__sendRequest("system sntp")
    def setSntpSettings(self,enable=True,sntpServer="time.nist.gov"):
        if enable:
            command = "enable"
        else:
            command = "disable"
        self.__sendRequest("system sntp " + " " + sntpServer)
    
    def setSystemTime(self,dt):
        self.__sendRequest("system time " + dt.strftime("%Y/%m/%d,%H:%M:%S") )
    def getSystemTime(self):
        return self.__sendRequest("system time")
    
    def getSystemTimezone(self):
        return float(int(self.__sendRequest("system timezone")))/3600.0
    def setSystemTimezone(self,hoursOffset):
        self.__sendRequest("system timezone " + str(math.ceil(hoursOffset*3600.0)))
    
    def setPort(self,number,port):
        self.__ports[number] = port
    
    def getPort(self,number):
        self.updatePortsStatus()
        return self.__ports[number]
    
    def getAllPorts(self):
        self.updatePortsStatus()
        return self.__ports
    
    def updatePortsStatus(self):
        ports = []
        powerOnStatus = self.getPortList()
        for i in range(4):
            status_splitter = shlex.shlex(self.getPortSetup(i), posix=True)
            status_splitter.whitespace_split = True
            ports.append( list(status_splitter) )
            self.__ports[i].setName(ports[i][0].replace("\"",""))
            self.__ports[i].setPowerOnAfterPowerLoss(bool(int(ports[i][3])))
            self.__ports[i].setPowerOn(bool(int(powerOnStatus[i])))
            self.__ports[i].setManualMode(ports[i][1]=="manual")
            self.__ports[i].setInterruptDelay(int(ports[i][2]))
            #still missing: setWatchdogOn
    
    # generic method to send requests to the NET-IO 230A and checking the response
    def __sendRequest(self,request,complainIfAnswerNot250=True):
        self.__s.send(request+"\n")
        data = self.__s.recv(self.__bufsize)
        if re.search("^250 ", data) == None and complainIfAnswerNot250:
            raise NameError("Error while sending request: " + request + "\nresponse from NET-IO 230A is:  " + data)
            return None
        else:
            return data.replace("250 ","").replace("\r\n","")
    
    def disconnect(self):
	    # close the socket:
        self.__s.close()
    
    def __del__(self):
        self.disconnect()
    ###   end of class netio230a   ----------------



class port(object):

    def __init__(self):
        self.__name = ""
        self.__manualMode = True #  False  means  timer mode
        self.__powerOn = False
        self.__watchdogOn = False
        self.__interruptDelay = 2
    
    def setManualMode(self,manualMode=True):
        self.__manualMode = manualMode
    def getManualMode(self):
        return self.__manualMode
    
    def setPowerOnAfterPowerLoss(self,powerOn=False):
        self.__powerOnAfterPowerLoss = powerOn
    def getPowerOnAfterPowerLoss(self):
        return self.__powerOnAfterPowerLoss
    
    def setTimerMode(self,timerMode):
        self.__manualMode = not timerMode
    def getTimerMode(self):
        return not self.__manualMode
    
    def setPowerOn(self,powerOn = False):
        self.__powerOn = powerOn
    def getPowerOn(self):
        return self.__powerOn
    
    def setName(self,newName):
        self.__name = newName
    def getName(self):
        return self.__name
    
    def setInterruptDelay(self,interruptDelay):
        self.__interruptDelay = interruptDelay
    def getInterruptDelay(self):
        return self.__interruptDelay
    
    def setWatchdogOn(self,watchdogOn):
        self.__watchdogOn = watchdogOn
    def getWatchdogOn(self):
        return self.__watchdogOn
    
