#! /usr/bin/env python
# -*- encoding: UTF8 -*-

# Philipp Klaus, philipp.l.klaus AT web.de
# The code is published under the terms of the GPL v.3

# example how to use the netio230a class

## import the netio230a class:
import netio230a
## for debugging (set debug mark with pdb.set_trace() )
import pdb


host = "192.168.1.2"
pw = "your choosen password"

def main():
    netio = netio230a.netio230a(host, "admin", pw, True)
    netio.connect()
    portList = netio.portList()
    netio.disconnect()
    
    # response anzeigen
    print "Port List: %s" % (portList),
    

if __name__ == '__main__':
    main()

