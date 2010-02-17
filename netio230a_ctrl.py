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



#  Command Line Interface - CLI  for the Koukaam NETIO 230A

## import the netio230a class:
import netio230a
## for sys.exit(1)
import sys
EXIT_SUCCESS=0
EXIT_FAILURE=1

## for ^C catching:
import signal

## for optparse.OptionParser()
import optparse

NOT_SET="--not set--"

def main():
    #p = optparse.OptionParser(usage="usage: %prog [options] -i[source] -o[target]",add_help_option=False)
    p = optparse.OptionParser(usage="usage: %prog [--host HOST] [--port PORT] [--username USERNAME] [--password PASSWORD] -s SOCKET [--on]",add_help_option=False)
    
    p.add_option('-?', action="store_true", help="show this help message and exit", dest="show_help")
    p.add_option('--host', '-h', default=NOT_SET, help="Hostname for the device (defaults to the first one found by the discovery in your LAN)")
    p.add_option('--port', '-p', default="1234", help="TCP port (defaults to 1234)")
    p.add_option('--username', '-u', default="admin", help="username to use for login (defaults to admin)")
    p.add_option('--password', '-w', default="", help="password to use for login (will ask if left empty)")
    p.add_option('--socket', '-s', default=NOT_SET, metavar="SOCKET#", help="socketnumber (1-4) to switch on/off")
    p.add_option("--on", action="store_true", dest="switchOn", help='switch on when --on set, off if omitted')
    
    options, arguments = p.parse_args()
    
    if options.host == NOT_SET and options.socket == NOT_SET:
        options.show_help = True
    
    if options.show_help:
        p.print_help()
        sys.exit(1)
    
    if options.switchOn == None:
        options.switchOn = False
    
    if options.host is NOT_SET:
        netio230a_devices = netio230a.get_all_detected_devices()
        if len(netio230a_devices) == 0:
            p.error("Please specify a host you want to connect to")      
        elif len(netio230a_devices) == 1:
            deviceName = netio230a_devices[0][0]
            ip = netio230a_devices[0][1]
            ip = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3])
            print "We discovered a single NETIO-230A device on the LAN: (%s,%s)" % (deviceName, ip)
            print "Selecting this one as host."
            options.host = ip
        else:
            print netio230a_devices
            addresses = ", ".join([ ("%s: %d.%d.%d.%d" % (dev[0], dev[1][0], dev[1][1], dev[1][2], dev[1][3])) for dev in netio230a_devices])
            print addresses
            p.error("%d devices found (%s).\nPlease specify which one you want to connect to using the --host parameter." % (len(netio230a_devices), addresses) )
    
    if options.socket is "not set":
        p.error("Please specify the socket you want to switch.")
    
    try:
        options.port = int(options.port)
    except StandardError:
        p.error("Please specify the TCP port to connect to as an integer value.")
    
    try:
        options.socket = int(options.socket)
    except StandardError:
        p.error("Please specify the socket to switch as an integer value.")
    
    if len(options.password) == 0:
        options.password = raw_input("Please give a password (user "+options.username+"): ")
    
    try:
        netio = netio230a.netio230a(options.host, options.username, options.password, True, options.port)
    except NameError, error:
        print("Could not connect. "+str(error))
        sys.exit(EXIT_FAILURE)
    #except StandardError, error:
    #    print("Could not connect. Please inform the programmer of this error. "+str(error))
    #    sys.exit(EXIT_FAILURE)
    try:
        netio.setPowerSocketPower(options.socket, int(options.switchOn))
    except StandardError, ne:
        print("Could not switch socket power. "+str(ne))
    
    netio = None
    
    # print response
    print "\n--------- successfully interfaced the Koukaam NETIO 230A ---------"
    print "set socket %s to: \"%s\"" % (options.socket, int(options.switchOn))
    print "---------------------------------------------------------------- \n"
    sys.exit(EXIT_SUCCESS)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL) # ^C exits the application
    
    main()


