#!/usr/bin/env python
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



# example how to use the netio230a class

## import the netio230a class:
import netio230a
## for sys.exit(1)
import sys


host = "192.168.1.2"
pw = "your choosen password"
port = 23

portToChange=2
portOn=True

def main():
    try:
        netio = netio230a.netio230a(host, "admin", pw, True, port)
    except StandardError:
        print("could not connect")
        sys.exit(1)
    portPowerBefore = netio.getPortList()
    netio.setPortPower(portToChange,portOn)
    portPowerAfter = netio.getPortList()
    
    netio = None
    
    # print response
    print "\n--------- successfully queried the Koukaam NETIO 230A ---------"
    print "power status before change:  port 1: %s, port 2: %s, port 3: %s, port 4: %s" % (portPowerBefore[0],portPowerBefore[1],portPowerBefore[2],portPowerBefore[3] )
    print "set port %s to: \"%s\"" % (portToChange,portOn)
    print "power status after change:  port 1: %s, port 2: %s, port 3: %s, port 4: %s" % (portPowerAfter[0],portPowerAfter[1],portPowerAfter[2],portPowerAfter[3] )
    print "---------------------------------------------------------------- \n"
    

if __name__ == '__main__':
    main()


