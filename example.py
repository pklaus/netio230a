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
## for debugging (set debug mark with pdb.set_trace() )
import pdb
## for sys.exit(1)
import sys


host = "192.168.1.2"
pw = "your choosen password"

def main():
    try:
        netio = netio230a.netio230a(host, "admin", pw, True)
    except StandardError:
        print("could not connect")
        sys.exit(1)
    version = netio.getFirmwareVersion()
    swDelay = netio.getSwitchDelay()
    ports = netio.getAllPorts()
    port1Status = netio.getPortSetup(0)
    deviceAlias = netio.getDeviceAlias()
    watchdogSettings1 = netio.getWatchdogSettings(1)
    networkSettings = netio.getNetworkSettings()
    netio = None
    
    # print response
    print "\n--------- successfully queried the Koukaam NETIO 230A ---------"
    print "power status:  port 1: %s, port 2: %s, port 3: %s, port 4: %s" % (ports[0].getPowerOn(),ports[1].getPowerOn(),ports[2].getPowerOn(),ports[3].getPowerOn())
    print "power on after power loss:  port 1: %s, port 2: %s, port 3: %s, port 4: %s" % (ports[0].getPowerOnAfterPowerLoss(),ports[1].getPowerOnAfterPowerLoss(),ports[2].getPowerOnAfterPowerLoss(),ports[3].getPowerOnAfterPowerLoss())
    print "port names:  port 1: \"%s\", port2: \"%s\", port 3: \"%s\", port 4: \"%s\"" % (ports[0].getName(),ports[1].getName(),ports[2].getName(),ports[3].getName())
    print "manual mode:  port 1: %s, port 2: %s, port 3: %s, port 4: %s" % (ports[0].getManualMode(),ports[1].getManualMode(),ports[2].getManualMode(),ports[3].getManualMode())
    print "interrupt delay:  port 1: %s seconds, port 2: %s seconds, port 3: %s seconds, port 4: %s seconds" % (ports[0].getInterruptDelay(),ports[1].getInterruptDelay(),ports[2].getInterruptDelay(),ports[3].getInterruptDelay())
    print "Firmware Version: %s" % (version)
    print "switch delay: %s seconds" % (swDelay)
    print "status of port 1: %s" % (port1Status)
    print "device alias: %s" % (deviceAlias)
    print "watchdog settings for port 1: %s" % (watchdogSettings1)
    print "network settings: %s" % (networkSettings)
    print "---------------------------------------------------------------- \n"
    

if __name__ == '__main__':
    main()


