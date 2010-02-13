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
tcp_port = 23


def main():
    try:
        netio = netio230a.netio230a(host, "admin", pw, True, tcp_port)
    except StandardError:
        print("could not connect")
        sys.exit(1)
    version = netio.getFirmwareVersion()
    swDelay = netio.getSwitchDelay()
    power_sockets = netio.getAllPowerSockets()
    power_socket_1_status = netio.getPowerSocketSetup(0)
    deviceAlias = netio.getDeviceAlias()
    watchdogSettings1 = netio.getWatchdogSettings(1)
    networkSettings = netio.getNetworkSettings()
    dnsServer = netio.getDnsServer()
    systemDiscoverable = netio.getSystemDiscoverableUsingTool()
    sntpSettings = netio.getSntpSettings()
    systemTime = netio.getSystemTime()
    timezoneOffset = netio.getSystemTimezone()
    
    netio = None
    
    # print response
    print "\n--------- successfully queried the Koukaam NETIO 230A ---------"
    print "power status:  power socket 1: %s, power socket 2: %s, power socket 3: %s, power socket 4: %s" % (power_sockets[0].getPowerOn(),power_sockets[1].getPowerOn(),power_sockets[2].getPowerOn(),power_sockets[3].getPowerOn())
    print "power on after power loss:  power socket 1: %s, power socket 2: %s, power socket 3: %s, power socket 4: %s" % (power_sockets[0].getPowerOnAfterPowerLoss(),power_sockets[1].getPowerOnAfterPowerLoss(),power_sockets[2].getPowerOnAfterPowerLoss(),power_sockets[3].getPowerOnAfterPowerLoss())
    print "power socket names:  power socket 1: \"%s\", power socket2: \"%s\", power socket 3: \"%s\", power socket 4: \"%s\"" % (power_sockets[0].getName(),power_sockets[1].getName(),power_sockets[2].getName(),power_sockets[3].getName())
    print "manual mode:  power socket 1: %s, power socket 2: %s, power socket 3: %s, power socket 4: %s" % (power_sockets[0].getManualMode(),power_sockets[1].getManualMode(),power_sockets[2].getManualMode(),power_sockets[3].getManualMode())
    print "interrupt delay:  power socket 1: %s seconds, power socket 2: %s seconds, power socket 3: %s seconds, power socket 4: %s seconds" % (power_sockets[0].getInterruptDelay(),power_sockets[1].getInterruptDelay(),power_sockets[2].getInterruptDelay(),power_sockets[3].getInterruptDelay())
    print "Firmware Version: %s" % (version)
    print "switch delay: %s seconds" % (swDelay)
    print "status of power socket 1: %s" % (power_socket_1_status)
    print "device alias: %s" % (deviceAlias)
    print "watchdog settings for power socket 1: %s" % (watchdogSettings1)
    print "network settings: %s" % (networkSettings)
    print "system discoverable: %s" % (systemDiscoverable)
    print "DNS server: %s" % (dnsServer)
    print "SNTP settings: %s" % (sntpSettings)
    print "system time: %s" % (systemTime)
    print "timezone offset: %s hours" % (timezoneOffset)
    
    print "---------------------------------------------------------------- \n"
    

if __name__ == '__main__':
    main()


