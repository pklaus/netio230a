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
tcp_port = 23

power_socket_to_change=2
power_on=True

def main():
    try:
        netio = netio230a.netio230a(host, "admin", pw, True, tcp_port)
    except StandardError:
        print("could not connect")
        sys.exit(1)
    power_before = netio.getPowerSocketList()
    netio.setPowerSocketPower(power_socket_to_change,power_on)
    power_after = netio.getPowerSocketList()
    
    netio = None
    
    # print response
    print "\n--------- successfully queried the Koukaam NETIO 230A ---------"
    print "power status before change:  power socket 1: %s, power socket 2: %s, power socket 3: %s, power socket 4: %s" % (power_before[0],power_before[1],power_before[2],power_before[3] )
    print "set power socket %s to: \"%s\"" % (power_socket_to_change,power_on)
    print "power status after change:  power socket 1: %s, power socket 2: %s, power socket 3: %s, power socket 4: %s" % (power_after[0],power_after[1],power_after[2],power_after[3] )
    print "---------------------------------------------------------------- \n"
    

if __name__ == '__main__':
    main()


