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


import netio230a
import sys
EXIT_SUCCESS=0
EXIT_FAILURE=1


# callback function for any found NETIO-230A device:
def print_netio230a_device(device):
    deviceName = device[0]
    ip = device[1]
    sm = device[2]
    gw = device[3]
    mac = device[4]
    answer_time = device[5]
    
    print "\nUPD answer in %.2f ms" % answer_time
    print "Found a Koukaam NETIO-230A:"
    print "Name is:", deviceName
    print "IP address:", "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3])
    print "Subnet Mask:", "%s.%s.%s.%s" % (sm[0], sm[1], sm[2], sm[3])
    print "Gateway address:", "%s.%s.%s.%s" % (gw[0], gw[1], gw[2], gw[3])
    print "MAC address:", "%02X:%02X:%02X:%02X:%02X:%02X\n" % (mac[0], mac[1], mac[2], mac[3], mac[4], mac[5])
    
    global totalCount
    totalCount += 1

if __name__ == '__main__':
    print "Trying to discover any Koukaam NETIO-230A available on your LAN"
    totalCount = 0
    
    netio230a.discover_netio230a_devices(print_netio230a_device)
    
    if totalCount == 0:
        print "No Koukaam NETIO-230A device found on your network."
        sys.exit(EXIT_FAILURE)
    else:
        print "Exiting after having found a number of %s Koukaam NETIO-230A devices." % totalCount
        sys.exit(EXIT_SUCCESS)

