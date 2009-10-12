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


class UDPintsockThread(threading.Thread):
    def __init__ (self,port):
        threading.Thread.__init__(self)
        self.__port = port
    def run(self):
        addr = ('', self.__port)
        # Create socket and bind to address
        UDPinsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDPinsock.bind(addr)
        UDPinsock.settimeout(3)
        # Receive messages
        while True:
            try:
                data, addr = UDPinsock.recvfrom(1024)
            except:
                #print "server timeout"
                break
            if data.find("IPCam") == 0:
                deviceName = data[38:38+16]
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
                print "UPD answer from:" , addr[0]
                print "Found a Koukaam NETIO-230A:"
                print "Name is:", deviceName
                print "IP address:", "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3])
                print "Subnet Mask:", "%s.%s.%s.%s" % (sm[0], sm[1], sm[2], sm[3])
                print "Gateway address:", "%s.%s.%s.%s" % (gw[0], gw[1], gw[2], gw[3])
                print "MAC address:", "%x:%x:%x:%x:%x:%x" % (mac[0], mac[1], mac[2], mac[3], mac[4], mac[5])
                print
        UDPinsock.close()

if __name__ == '__main__':
    
    print "Trying to discover any Koukaam NETIO-230A available on your LAN"
    
    # sends the request to ask for available NETIO-230A on the network (bytes sniffed using wireshark)
    request = "PCEdit\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00"
    request += "\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    request += "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    port = 4000

    dest = ('<broadcast>',port)
    #dest = ('255.255.255.255',port)


    myUDPintsockThread = UDPintsockThread(port)
    myUDPintsockThread.start()
    
    
    UDPoutsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # to allow broadcast communication:
    UDPoutsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    UDPoutsock.sendto(request, dest)
    
    myUDPintsockThread.join()



