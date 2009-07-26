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



# example how to use the netio230a class

## import the netio230a class:
import netio230a
## for debugging (set debug mark with pdb.set_trace() )
import pdb


host = "192.168.1.2"
pw = "your choosen password"

def main():
    netio = netio230a.netio230a(host, "admin", pw, True)
    netio.login()
    portList = netio.getPortStatus()
    version = netio.getFirmwareVersion()
    #swDelayBefore = netio.getSwitchDelay()
    #netio.setSwitchDelay(1.5)
    #swDelayAfter = netio.getSwitchDelay()
    swDelay = netio.getSwitchDelay()
    allPorts = netio.getAllPorts()
    deviceAlias = netio.getDeviceAlias()
    watchdogSettings1 = netio.getWatchdogSettings(1)
    networkSettings = netio.getNetworkSettings()
    netio = None
    
    # print response
    print "Ports:  port 1 %s, port2 %s, port 3 %s, port 4 %s" % (allPorts.getPort1().getPortSwitchedOn(),allPorts.getPort2().getPortSwitchedOn(),allPorts.getPort3().getPortSwitchedOn(),allPorts.getPort4().getPortSwitchedOn())
    print "Ports:  port 1 %s, port2 %s, port 3 %s, port 4 %s" % (portList[0],portList[1],portList[2],portList[3])
    print "Firmware Version: %s" % (version),
    #print "switch delay before: %s" % (swDelayBefore),
    #print "switch delay after: %s" % (swDelayAfter),
    print "switch delay: %s" % (swDelay),
    print "device alias: %s" % (deviceAlias),
    print "watchdog settings for port 1: %s" % (watchdogSettings1),
    print "network settings: %s" % (networkSettings),

    

if __name__ == '__main__':
    main()


