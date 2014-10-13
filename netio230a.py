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


#  ,--------------------------------------------------------------------------------.
#  |                                                                                |
#  |          __________________________________________________________            |
#  |         /                                                          \           |
#  |        /                                Artwork by Philipp Klaus    \          |
#  |       /                                                              \         |
#  |      /                                                                \        |
#  |     /                                                                  \       |
#  |    /                                                                    \      |
#  |   .----------------------------------------------------------------------.     |
#  |   |  NETIO-230A     Output        RS-232C     AUX           Network      |     |
#  |   |                                                 on/off     __        |     |
#  |   |               .  .  .  .    O\'''''''/O   ...    _  _     |  |       |     |
#  |   |                               '''''''     | |   |_||_|    |,,|       |     |
#  |   \               1  2  3  4                  '''                        |     |
#  |    `-._______________________________________________________________,,--'     |
#  |                                                                                |
#  | This class represents the multiple plug hardware Koukaam NET-IO 230A.          |
#  | It can be configured using raw TCP communication.                              |
#  | The class aimes at providing complete coverage of the functionality of the box |
#  | but not every action is supported yet.                                         |
#  |                                                                                |
#  |      -------- ToDo next ------------                                           |
#  |  * http://koukaam.se/koukaam/forum/viewthread.php?forum_id=18&thread_id=399    |
#  |  * Command for enable wd with 360s delay on output 2:                          |
#  |  * port wd 2 enable 192.168.10.101 10 360 1 3 enable enable                    |
#  |                                                                                |
#  `--------------------------------------------------------------------------------'


#For PyS60 we need this:
try:
    import sys
    # http://discussion.forum.nokia.com/forum/showthread.php?p=575213
    # Try to import 'btsocket' as 'socket' (just for 1.9.x)
    if sys.platform == 'symbian_s60':
        sys.modules['socket'] = __import__('btsocket')
except ImportError:
    pass
# for the raw TCP socket connection:
import socket
# For a better handling of socket communication (Is data available? Or the socket closed?):
import select
# We also need threads to watch the socket for FINs (remote disconnects)
import threading
# for md5 checksum:
try:
    import hashlib
except ImportError:
    # for Python << 2.5
    import md5
# for RegularExpressions:
import re
## for debugging (set debug mark with pdb.set_trace() )
#import pdb
# for math.ceil()
import math
# for shlex.shlex() (to parse answers from the NETIO 230A)
import shlex
# for errno codes (cf. <http://docs.python.org/library/errno.html>)
import errno

import time
### for date.today()
#from datetime import date
from datetime import datetime, timedelta

TELNET_LINE_ENDING = "\r\n"
TELNET_SOCKET_TIMEOUT = 5
INITIAL_WAIT_FOR_OTHER_REQUEST = 0.013 # 13 ms to wait for other requests to terminate (later requests use the mean request time)
#ANTI_FLOODING_WAIT = 0.001 # wait 1 ms before sending the next request (after having received the last response)
ANTI_FLOODING_WAIT = 0.0
MAX_NUMBER_OF_REQUESTS_BEFORE_RECONNECT = 500
# The time we wait until we start monitoring the status of the socket
WATCH_SOCKET_WAIT = 10.
WATCH_WAKE_TIME = 0.2
MAX_SECONDS_WAIT_FOR_RECEIVE = 1.0
MAX_SECONDS_WAIT_FOR_RECEIVE_HELLO = MAX_SECONDS_WAIT_FOR_RECEIVE * 3
TIMES_WAIT_FOR_RECEIVE = 100

class netio230a(object):
    """netio230a is the basic class that you want to instantiate when communicating
    with the Koukaam NETIO 230A. It can handle the raw TCP socket connection and
    helps you send the commands to switch on / off powerSockets etc."""

    def __init__(self, host, username, password, secureLogin=False, customTCPPort=23):
        """netio230a constructor: set up an instance of netio230a by giving:

            host        the hostname of the NETIO-230A (may be in the form of something.dyndns.org or 192.168.1.2)
            username    the username you want to use to authenticate against the NETIO-230A
            password    the password (that belongs to username)
            secureLogin bool value specifying whether to use a hashed or a cleartext login. True is hightly recommended for insecure networks!
            customTCPPort  integer specifying which port to connect to, defaul: 23 (NETIO-230A must be reachable via KSHELL/telnet via hostname:customTCPPort)
        """
        self.logging = False
        self.__lock = threading.Lock()
        self.mean_request_time = INITIAL_WAIT_FOR_OTHER_REQUEST
        self.number_of_sent_requests = 0
        self.__last_request_received = time.time()
        self.__host = host
        self.__username = username
        self.__password = password
        self.__secureLogin = secureLogin
        self.__tcp_port = customTCPPort
        self.__bufsize = 1024
        self.__power_sockets = [ PowerSocket() for i in range(4) ]
        self.__create_socket_and_login()

    def __create_socket_and_login(self, lock_already_acquired = False):
        # create a TCP/IP socket
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try: # btsocket on PyS60 lacks this member function so we have to try it:
            self.__s.settimeout(TELNET_SOCKET_TIMEOUT)
        except:
            pass
        self.__login(lock_already_acquired)
        # Create the thread that watches for timeouts of the NETIO230A TCP connection:
        self.__watchSocketThread = threading.Timer(WATCH_SOCKET_WAIT, self.__watchSocket)
        # When the rest of the program terminates, the thread should stop as well:
        self.__watchSocketThread.daemon = True
        self.__watchSocketThread.start()


    def __login(self, lock_already_acquired = False):
        """Login to the server using the credentials given to the constructor.
           Note that this is a private method called by the constructor
           (so all connection details are set already)."""
        # connect to the server
        try:
            self.__s.connect((self.__host, self.__tcp_port))
            # wait for the answer
            data = self.__receive( MAX_SECONDS_WAIT_FOR_RECEIVE_HELLO )
        except StandardError, error:
            if type(error) == socket.timeout:
                raise NameError("Timeout while connecting to " + self.__host)
                #print("There was a timeout")
            elif type(error) == socket.gaierror or type(error) == socket.error and error.errno == errno.ENETUNREACH:
                raise NameError("Unable to understand the host you gave: %s. Please provide a correct IP address or domain name." % self.__host)
            elif type(error) == socket.error:
                if error.errno == errno.ECONNREFUSED:
                    raise NameError("The connection was refused by the remote host. Possible errors: wrong IP or wrong TCP port given or the telnet server on the NETIO-230A crashed.")
                elif error.errno == errno.EHOSTUNREACH:
                    raise NameError("There is no route to the host given: " + self.__host)
                elif error.errno == errno.ECONNRESET:
                    raise NameError("The connection was reset by the device. This is usually the case when you still have another network socket connected to the device. It may also be the case when the telnet server on the device crashed. In this case reboot the device (if possible & sensible).")
            # in any other case just hand on the risen error:
            raise error
        except Exception, error:
            raise error

        # The answer should be in the form     "100 HELLO E675DDA5"
        # where the last eight letters are random hexcode used to hash the password
        if self.__reSearch("^100 HELLO [0-9A-F]{8}"+TELNET_LINE_ENDING+"$", data) == None and \
           self.__reSearch("^100 HELLO [0-9A-F]{8} - KSHELL V1.1"+TELNET_LINE_ENDING+"$", data) == None and \
           self.__reSearch("^100 HELLO [0-9A-F]{8} - KSHELL V1.2"+TELNET_LINE_ENDING+"$", data) == None and \
           self.__reSearch("^100 HELLO [0-9A-F]{8} - KSHELL V1.3"+TELNET_LINE_ENDING+"$", data) == None :
            raise NameError("Error while connecting: Not received a \"100 HELLO ... signal from the remote device. Maybe not a NET-IO 230A?")
        if self.__secureLogin:
            hash=str(data).split(" ")[2]
            msg=self.__username + self.__password + hash
            # for md5 checksum:
            try:
                md = hashlib.md5()
            except:
                md = md5.new()
            md.update(msg.encode("ascii"))
            loginString = "clogin " + self.__username + " " + md.hexdigest() + TELNET_LINE_ENDING
        else:
            # use the password in cleartext
            loginString = "login " + self.__username + " " + self.__password + TELNET_LINE_ENDING
        try:
            # send login string and wait for the answer
            response = self.__sendRequest(loginString, True, lock_already_acquired)
        except NameError, error:
            self.disconnect()
            try:
                problem = str(error).partition('\n\n')[2]
            except:
                problem = "?"
            if problem.find("502 UNKNOWN COMMAND") != -1:
                raise NameError("Error while connecting: Login failed with message 502 UNKNOWN COMMAND. This is usually the case when the telnet server crashed. Reboot the NETIO-230A device to get it up running again.")
            elif problem.find("501 INVALID PARAMETER") != -1:
                raise NameError("Error while connecting: Login failed with message 501 INVALID PARAMETER. This is usually the case when the telnet server crashed. Reboot the NETIO-230A device to get it up running again.")
            elif problem.find("504 ALREADY LOGGED IN") != -1:
                raise NameError("You are already logged in. Something strange happened.")
            else:
                raise NameError("Error while connecting: Login failed; " + str(error).partition('\n\n')[2])
        except StandardError, error:
            self.disconnect()
            raise NameError("Error while connecting: Login failed; " + str(error))

    def __watchSocket(self):
        try:
            assert self.__s
            inputs = [self.__s]
            outputs = [self.__s]
            while True:
                if ( time.time() - self.__last_request_received ) < WATCH_SOCKET_WAIT:
                    time.sleep(WATCH_SOCKET_WAIT - (time.time()-self.__last_request_received))
                else:
                    time.sleep(WATCH_WAKE_TIME)
                if not self.connected():
                    continue
                # If a request is pending, no action should be required:
                if not self.__lock.acquire(False):
                    continue
                try:
                    readable, writable, exceptional = select.select(inputs, outputs, inputs)
                    # If the socket has something to be read (no blocking -
                    # guaranteed) we want to know what strange thing this is:
                    if self.__s in readable:
                        answ = self.__s.recv(self.__bufsize)
                        if self.__reSearch("^130 CONNECTION TIMEOUT", answ):
                            self.log("The NETIO230A wants to close the connection due to a timeout. We'll respect that.")
                        elif len(answ) == 0 :
                            self.log("The NETIO230A has closed the connection. We do the same now.")
                            break
                        else:
                            raise NameError("The NETIO230A sent a response when we didn't expect any: " + answ)
                except:
                    pass
                finally:
                    self.__lock.release()

        finally:
            self.__shutdownSocket()

    def __reSearch(self, regexp, data):
        return re.search(regexp.encode("ascii"), data)

    def enable_logging(self, log_file):
        self.logging = True
        self.log_file = log_file
        try:
            self.log("Logging started on %s." % datetime.now().isoformat())
        except StandardError, error:
            self.logging = True
            raise error

    def log(self, message, line_break=True):
        if self.logging:
            self.log_file.write("%s %s%s" % (datetime.now().isoformat(), message, "\n" if line_break else "") )
            # or if the ternary operator is not available:
            #n=""
            #if line_break:
            #    n = "\n"
            #self.log_file.write("%s %s%s" % (datetime.now().isoformat(), message, n) )

    def getPowerSocketList(self):
        """Sends request to the NETIO 230A to ask for the power socket status.

        'port list' returns a string (4 chars long) specifying which power sockets are switched on/off.
        Each char is representing the power status of one power socket: 0/1
        We convert them to a list of four boolean values: """
        return [bool(int(status)) for status in self.__sendRequest("port list")]

    def getPowerSocketSetup(self,power_socket):
        """Sends request to the NETIO 230A to ask for the setup of the power socket given as parameter.
        returns the "port setup" string as specifyed by Koukaam"""
        return self.__sendRequest("port setup " + str(power_socket+1))

    def setPowerSocketPower(self,power_socket,switchOn=False):
        """setPowerSocketPower(power_socket,switchOn=False): method to set the power status of the power socket specified by the argument power_socket to the bool argument switchOn
        returns nothing"""
        # the type conversion of switchOn ensures that the values are either "0" or "1":
        self.__sendRequest("port " + str(power_socket) + " " + str(int(bool(int(switchOn)))) )

    def togglePowerSocketPower(self,power_socket):
        """togglePowerSocketPower(power_socket): toggles the power status of power socket specified by the (one based) argument power_socket.
        returns a boolean indicating the new status"""
        previous_state = self.getPowerSocket(power_socket-1).getPowerOn() # the getPowerSocket() function has a zero based argument! therefore -1
        self.setPowerSocketPower(power_socket, not previous_state)
        return not previous_state

    def setPowerSocketTempInterrupt(self,power_socket):
        self.__sendRequest("port " + str(int(power_socket)) + " int" )

    def setPowerSocketManualMode(self,power_socket,manualMode=True):
        self.__sendRequest("port " + str(int(power_socket)) + " manual")

    def getFirmwareVersion(self):
        return self.__sendRequest("version")

    def getDeviceAlias(self):
        return self.__sendRequest("alias")

    def setDeviceAlias(self,alias = "netio230a"):
        self.__sendRequest("alias " + alias)

    # this command is operation-safe: it does not switch the power sockets on/off during reboot of the NETIO 230A
    def reboot(self):
        response = self.__sendRequest("reboot",False)
        if re.search("^120 Rebooting", response) != None:
            time.sleep(.05) # no reboot if disconnecting too soon

    def getWatchdogSettings(self,power_socket):
        return self.__sendRequest("port wd " + str(power_socket))

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
        """getSystemTime() returns a datetime object"""
        formatedTimestring = self.__sendRequest("system time")
        date = formatedTimestring.partition(",")[0].split("/")
        time = formatedTimestring.partition(",")[2].split(":")
        return datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]))

    def getSystemUptime(self):
        """getSystemUptime() returns a timedelta object"""
        formatedTimestring = self.__sendRequest('uptime')
        uptime_regex = r'^(?P<years>\d+) years (?P<days>\d+) days (?P<hours>\d+) hours (?P<min>\d+) min (?P<sec>\d+) sec$'

        try:
            g = re.search(uptime_regex, formatedTimestring).groupdict()
            return timedelta(days=int(g['days']), hours=int(g['hours']), minutes=int(g['min']), seconds=int(g['sec']))
        except AttributeError:
            return False

    def getSystemTimezone(self):
        """getSystemTimezone() returns the timezone offset from UTC in hours of the NETIO-230A."""
        return float(int(self.__sendRequest("system timezone")))/3600.0

    def setSystemTimezone(self,hoursOffset):
        """setSystemTimezone(hoursOffset) sets the timezone offset from UTC in hours of the NETIO-230A."""
        self.__sendRequest("system timezone " + str(math.ceil(hoursOffset*3600.0)))

    def setPowerSocket(self,number,power_socket):
        self.__power_sockets[number] = power_socket

    def getPowerSocket(self,number):
        self.updatePowerSocketsStatus()
        return self.__power_sockets[number]

    def getAllPowerSockets(self):
        self.updatePowerSocketsStatus()
        return self.__power_sockets

    def updatePowerSocketsStatus(self):
        power_sockets = []
        powerOnStatus = self.getPowerSocketList()
        for i in range(4):
            status_splitter = shlex.shlex(self.getPowerSocketSetup(i).encode('ascii'), posix=True)
            status_splitter.whitespace_split = True
            power_sockets.append( list(status_splitter) )
            self.__power_sockets[i].setName(power_sockets[i][0])
            self.__power_sockets[i].setPowerOnAfterPowerLoss(bool(int(power_sockets[i][3])))
            self.__power_sockets[i].setPowerOn(powerOnStatus[i])
            self.__power_sockets[i].setManualMode(power_sockets[i][1]=="manual")
            self.__power_sockets[i].setInterruptDelay(int(power_sockets[i][2]))
            #still missing: setWatchdogOn

    def __assureConnection(self):
        try:
            assert self.__s
        except:
            self.log("Socket not ready. Reconnecting.")
            # try to reconnect:
            self.__create_socket_and_login(True)

    def __disconnectAfterLargeNumberOfRequests(self):
        if MAX_NUMBER_OF_REQUESTS_BEFORE_RECONNECT > 0 and (self.number_of_sent_requests+1) % MAX_NUMBER_OF_REQUESTS_BEFORE_RECONNECT == 0:
            self.number_of_sent_requests += 1
            if not self.connected(): return
            print("%d requests made, reconnecting..." % MAX_NUMBER_OF_REQUESTS_BEFORE_RECONNECT)
            self.disconnect()

    def __acquireLockWaitForOtherRequestsToFinish(self):
        counter = 0
        # in this loop we want to avoid errors for concurrent requests (from different threads etc.)
        while True:
            got_lock = self.__lock.acquire(False)
            if got_lock:
                return True
            wait_time = self.mean_request_time*.5
            time.sleep(wait_time)
            counter += 1
            print("concurrent action for request: %s" % request)
            self.log("Waiting for an other request to finish. Average time for processes to finish is %.6f s after a total number of %d requests." % (self.mean_request_time, self.number_of_sent_requests) )
            if counter * wait_time >= 3 * (self.mean_request_time + ANTI_FLOODING_WAIT):
                # If we waited for too long, we give up.
                raise NameError("Sorry, some other process is sending a request you cannot send yours now.")
        return None


    def __waitFloodingProtect(self):
            if ANTI_FLOODING_WAIT > 0.0005 and time.time()-self.__last_request_received < ANTI_FLOODING_WAIT:
                time.sleep(ANTI_FLOODING_WAIT-(time.time()-self.__last_request_received))

    # generic method to send requests to the NET-IO 230A and checking the response
    def __sendRequest(self,request,complainIfAnswerNot250=True,lock_already_acquired=False):
        if not lock_already_acquired:
            assert self.__acquireLockWaitForOtherRequestsToFinish()
        self.__disconnectAfterLargeNumberOfRequests()
        self.__assureConnection()
        try:
            self.__waitFloodingProtect()
            starting_time = time.time()
            try:
                self.__send(request.encode("ascii")+TELNET_LINE_ENDING.encode("ascii"))
            except Exception, error:
                self.log("could not send the command: "+str(error))
                raise NameError("Sending the command '%s' produced this error: %s." % (request, error))
            try:
                data = self.__receive()
            except Exception, error:
                # maybe we should try to reconnect here too before giving up.
                self.log("trying to receive data failed: "+str(error))
                raise NameError("trying to receive data failed: "+str(error))
            if self.__reSearch("^250 ", data) == None and complainIfAnswerNot250:
                raise NameError("Error while sending request: " + request + "\nresponse from NET-IO 230A is:  " + data.replace(TELNET_LINE_ENDING,''))
            else:
                data = data.decode("ascii")
                data = data.replace("250 ","").replace(TELNET_LINE_ENDING,"")
                self.mean_request_time = ( self.number_of_sent_requests*self.mean_request_time + (time.time()-starting_time) ) / (self.number_of_sent_requests + 1)
                self.number_of_sent_requests += 1
                self.__last_request_received = time.time()
        finally:
            if not lock_already_acquired:
                self.__lock.release()
        return data

    def connected(self):
        if not self.__s: return False
        sock = self.__s
        if sock not in select.select([sock], [sock], [sock])[1]:
            return False
        return True

    def disconnect(self):
        if not self.connected(): return
        try:
            self.__watchSocketThread.cancel()
        except:
            pass
        try:
            # send the quit command to the box (if we have an open connection):
            self.__send("quit".encode("ascii")+TELNET_LINE_ENDING.encode("ascii"))
            self.__receive()  # should give  110 BYE
        except Exception, error:
            raise error
        finally:
            self.__shutdownSocket()

    def __shutdownSocket(self):
        time.sleep(.01)
        try:
            # Let's try to be nice and shut down the TCP connection correctly:
            self.__s.shutdown(socket.SHUT_WR)
        except:
            pass
        finally:
            # close the socket (if it is still open):
            try:
                self.__s.close()
            except:
                pass
        self.__s = None

    def __del__(self):
        try:
            self.disconnect()
        except:
            pass

    def __send(self, data):
        self.log(data, False)
        self.__s.send(data)

    def __receive(self, wait_time = MAX_SECONDS_WAIT_FOR_RECEIVE):
        assert self.__s
        sock = self.__s
        start = time.time()
        while sock not in select.select([sock], [sock], [sock])[0]:
            time.sleep(wait_time/TIMES_WAIT_FOR_RECEIVE)
            if time.time() - start > wait_time:
                raise NameError("The NETIO230A did not answer in time (%.3f s)." % wait_time)
        response = sock.recv(self.__bufsize)
        if len(response)==0:
            self.__shutdownSocket()
            raise NameError("The NETIO230A is closing the connection unexpectedly")
        self.log(response, False)
        return response
    ###   end of class netio230a   ----------------


class PowerSocket(object):
    """ This is a class to represent the power sockets of the NETIO-230A. """

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



# ----------------------------------------------------------------
# logic and code to detect available NETIO-230A devices on the LAN

import socket
import threading
import array
import time
import sys

NETIO230A_UDP_DISCOVER_PORT = 4000
DETECTION_TIMEOUT=0.2 # should be enough. Usualy we get the answer in 4.6 ms
DEVICE_NAME_TERMINATION = "\x00\x30\x30\x38\x30"
# the request to ask for available NETIO-230A on the network (bytes sniffed using wireshark)
DISCOVER_REQUEST = "PCEdit\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00"
DISCOVER_REQUEST += "\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
DISCOVER_REQUEST += "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"


# thread to run the UDP server that listens to answering NETIOs on your network
class UDPintsockThread(threading.Thread):
    def __init__ (self,port,callback_for_found_devices):
        """ listens to answers from available NETIO-230A devices on the LAN and calls
            callback_for_found_devices([deviceName, ip, sm, gw, mac, answerTime])     """
        threading.Thread.__init__(self)
        self.__port = port
        self.__callback = callback_for_found_devices
        self.__startTime = time.time()
    def run(self):
        addr = ('', self.__port)
        # Create socket and bind to address
        UDPinsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDPinsock.bind(addr)
        # will listen for three seconds to your network
        UDPinsock.settimeout(DETECTION_TIMEOUT)
        while True:
            try:
                # Receive messages
                data, addr = UDPinsock.recvfrom(1024)
                # keep timestamp of arriving package
                answerTime=time.time()
            except:
                #print "server timeout"
                break
            # check if we found a NETIO-230A
            if data.find("IPCam") == 0 and len(data)== 61:
                # documentation of data is found on http://wiki.github.com/pklaus/netio230a/netdiscover-protocol
                deviceName = data[38:data.find(DEVICE_NAME_TERMINATION)]
                data = array.array('B', data)
                ip = []
                for n in range(0, 4):
                    ip.append(data[10+n])
                mac = [0,0,0,0,0,0]
                for n in range(0, 6):
                    mac[n] = data[14+n]
                sm = []
                for n in range(0, 4):
                    sm.append(data[20+n])
                gw = []
                for n in range(0, 4):
                    gw.append(data[27+n])
                device = [deviceName, ip, sm, gw, mac, (answerTime-self.__startTime)*1000]
                self.__callback(device)
        UDPinsock.close()


def discover_netio230a_devices(callback_for_found_devices):
    dest = ('<broadcast>',NETIO230A_UDP_DISCOVER_PORT)
    #dest = ('255.255.255.255',NETIO230A_UDP_DISCOVER_PORT)
    myUDPintsockThread = UDPintsockThread(NETIO230A_UDP_DISCOVER_PORT,callback_for_found_devices)
    myUDPintsockThread.start()

    # send on all interfaces of the computer:
    # cf. last lines of the comment <http://serverfault.com/questions/72112/how-to-fix-the-global-broadcast-address-255-255-255-255-behavior-on-windows/72152#72152>
    interfaces = all_interfaces()
    # but in case we could not enumerate all interfaces we still want one try:
    if len(interfaces) == 0: interfaces = [['','']]
    for interface in interfaces:
        UDPoutsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # to allow broadcast communication:
        UDPoutsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #if interface[1]=='':
        #    host = ""
        #else:
        #    host = socket.inet_ntoa(interface[1])
        #UDPoutsock.bind((host, 0))
        # or using the ternary operator:
        UDPoutsock.bind(("" if interface[1]=='' else socket.inet_ntoa(interface[1]), 0))
        # send UDP broadcast:
        UDPoutsock.sendto(DISCOVER_REQUEST, dest)
    myUDPintsockThread.join()

## http://code.activestate.com/recipes/439093/#c1
try:
    import fcntl
except:
    pass
import struct
import array
def all_interfaces():
    max_possible = 128  # arbitrary. raise if needed.
    bytes = max_possible * 32
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array('B', '\0' * bytes)
    try:
        outbytes = struct.unpack('iL', fcntl.ioctl(
            s.fileno(),
            0x8912,  # SIOCGIFCONF
            struct.pack('iL', bytes, names.buffer_info()[0])
        ))[0]
    except:
        return []
    namestr = names.tostring()
    lst = []
    for i in range(0, outbytes, 40):
        name = namestr[i:i+16].split('\0', 1)[0]
        ip   = namestr[i+20:i+24]
        lst.append((name, ip))
    return lst

all_devices=[]
def device_detected_callback(device):
    global all_devices
    all_devices.append(device)

# if any software module wants to get all found devices with one call (blocking) then this function can be used:
def get_all_detected_devices():
    global all_devices
    all_devices = []
    discover_netio230a_devices(device_detected_callback)
    return all_devices
