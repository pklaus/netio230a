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

## for optparse.OptionParser()
import optparse



def main():
    p = optparse.OptionParser()
    
    p.add_option('--password', '-w', default="not set")
    p.add_option('--host', '-n', default="not set")
    p.add_option('--username', '-u', default="admin")
    p.add_option('--port', '-p', default="world")
    p.add_option("--on", action="store_true", dest="switchOn", help='switch on when --on set, off if omitted')
    
    options, arguments = p.parse_args()
    
    if options.switchOn == None:
        options.switchOn = False
    
    if options.password is not "not set" and options.host is not "not set":
    
        try:
            netio = netio230a.netio230a(options.host, options.username, options.password, True)
        except StandardError:
            print("could not connect")
            sys.exit(1)
        netio.setPortPower(options.port, int(options.switchOn) )
        
        netio = None
        
        # print response
        print "\n--------- successfully interfaced the Koukaam NETIO 230A ---------"
        print "set port %s to: \"%s\"" % (options.port, int(options.switchOn))
        print "---------------------------------------------------------------- \n"
        
    else:
        p.print_help()


if __name__ == '__main__':
    main()


