#!/usr/bin/env python
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



import socket
import threading
import array
import time
import sys



EXIT_SUCCESS=0
EXIT_FAILURE=1
NETIO230A_UDP_DISCOVER_PORT = 4000
DEVICE_NAME_TERMINATION = "\x00\x30\x30\x38\x30"


# thread to run the UDP server that listens to answering NETIOs on your network
class UDPintsockThread(threading.Thread):
    # custom contructor
    def __init__ (self,port):
        threading.Thread.__init__(self)
        self.__port = port
    def run(self):
        addr = ('', self.__port)
        # Create socket and bind to address
        UDPinsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDPinsock.bind(addr)
        # will listen for three seconds to your network
        UDPinsock.settimeout(3)
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
                print
                print "UPD answer in %.2f ms from: %s " % ((answerTime-startTime)*1000,addr[0])
                print "Found a Koukaam NETIO-230A:"
                print "Name is:", deviceName
                print "IP address:", "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3])
                print "Subnet Mask:", "%s.%s.%s.%s" % (sm[0], sm[1], sm[2], sm[3])
                print "Gateway address:", "%s.%s.%s.%s" % (gw[0], gw[1], gw[2], gw[3])
                print "MAC address:", "%02X:%02X:%02X:%02X:%02X:%02X" % (mac[0], mac[1], mac[2], mac[3], mac[4], mac[5])
                print
                global totalCount
                totalCount += 1
        UDPinsock.close()

# http://code.activestate.com/recipes/439093/#c1import socket
import fcntl
import struct
import array
def all_interfaces():
    max_possible = 128  # arbitrary. raise if needed.
    bytes = max_possible * 32
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array('B', '\0' * bytes)
    outbytes = struct.unpack('iL', fcntl.ioctl(
        s.fileno(),
        0x8912,  # SIOCGIFCONF
        struct.pack('iL', bytes, names.buffer_info()[0])
    ))[0]
    namestr = names.tostring()
    lst = []
    for i in range(0, outbytes, 40):
        name = namestr[i:i+16].split('\0', 1)[0]
        ip   = namestr[i+20:i+24]
        lst.append((name, ip))
    return lst
def format_ip(addr):
    return str(ord(addr[0])) + '.' + \
           str(ord(addr[1])) + '.' + \
           str(ord(addr[2])) + '.' + \
           str(ord(addr[3]))


if __name__ == '__main__':
    
    print "Trying to discover any Koukaam NETIO-230A available on your LAN"
    
    # sends the request to ask for available NETIO-230A on the network (bytes sniffed using wireshark)
    request = "PCEdit\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00"
    request += "\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    request += "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    

    dest = ('<broadcast>',NETIO230A_UDP_DISCOVER_PORT)
    #dest = ('255.255.255.255',NETIO230A_UDP_DISCOVER_PORT)


    myUDPintsockThread = UDPintsockThread(NETIO230A_UDP_DISCOVER_PORT)
    myUDPintsockThread.start()
    
    
    # set number of found NETIO-230A devices to 0
    totalCount = 0
    # set start time
    startTime = time.time()
    # send on all interfaces of the computer:
    # cf. last lines of the comment <http://serverfault.com/questions/72112/how-to-fix-the-global-broadcast-address-255-255-255-255-behavior-on-windows/72152#72152>
    for interface in all_interfaces():
        UDPoutsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # to allow broadcast communication:
        UDPoutsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        host = format_ip(interface[1])
        UDPoutsock.bind((host, 0))
        # send UDP broadcast:
        UDPoutsock.sendto(request, dest)
    
    myUDPintsockThread.join()
    
    if totalCount == 0:
        print "No Koukaam NETIO-230A device found on your network."
        sys.exit(EXIT_FAILURE)
    else:
        print "Exiting after having found a number of %s Koukaam NETIO-230A devices." % totalCount
        sys.exit(EXIT_SUCCESS)

