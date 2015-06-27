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


""" Command Line Interface - CLI  for the Koukaam NETIO 230A """

import netio230a
import sys
import signal
import argparse

EXIT_SUCCESS=0
EXIT_FAILURE=1

# Fix for Python 2/3 compatibility
try:
    input = raw_input
except NameError:
    pass

def main():
    parser = argparse.ArgumentParser(description=__doc__, conflict_handler='resolve')
    parser.add_argument('--host', '-h', help="Hostname for the device (defaults to the first one found by the discovery in your LAN)")
    parser.add_argument('--port', '-p', type=int, default=1234, help="TCP port (defaults to 1234)")
    parser.add_argument('--username', '-u', default="admin", help="username to use for login (defaults to admin)")
    parser.add_argument('--password', '-w', help="password to use for login (will ask if left empty)")
    parser.add_argument('--socket', '-s', metavar="SOCKET#", help="socketnumber (1-4) to switch on/off", required=True)
    parser.add_argument("--on", action="store_true", help='switch on when --on set, off if omitted')
    args = parser.parse_args()

    if not args.host:
        netio230a_devices = netio230a.get_all_detected_devices()
        if len(netio230a_devices) == 0:
            parser.error("Please specify a host you want to connect to. Could not detect any automatically.")
        elif len(netio230a_devices) == 1:
            deviceName = netio230a_devices[0][0]
            ip = netio230a_devices[0][1]
            ip = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3])
            print("We discovered a single NETIO-230A device on the LAN: (%s,%s)" % (deviceName, ip))
            print("Selecting this one as host.")
            args.host = ip
        else:
            print(netio230a_devices)
            addresses = ", ".join([ ("%s: %d.%d.%d.%d" % (dev[0], dev[1][0], dev[1][1], dev[1][2], dev[1][3])) for dev in netio230a_devices])
            print(addresses)
            p.error("%d devices found (%s).\nPlease specify which one you want to connect to using the --host parameter." % (len(netio230a_devices), addresses) )

    if not args.password:
        args.password = input("Please give a password (user "+args.username+"): ")

    try:
        netio = netio230a.netio230a(args.host, args.username, args.password, True, args.port)
    except NameError as error:
        print("Could not connect. "+str(error))
        sys.exit(EXIT_FAILURE)
    try:
        netio.setPowerSocketPower(args.socket, int(args.on))
    except Exception as ne:
        print("Could not switch socket power. "+str(ne))

    netio = None

    print("\n--------- successfully interfaced the Koukaam NETIO 230A ---------")
    print("set socket %s to: \"%s\"" % (args.socket, int(args.on)))
    print("---------------------------------------------------------------- \n")
    sys.exit(EXIT_SUCCESS)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL) # ^C exits the application

    main()

