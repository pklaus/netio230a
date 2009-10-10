#!/usr/bin/env python
# -*- encoding: UTF8 -*-
 
# Author: Philipp Klaus, philipp.l.klaus AT web.de
 
 
# This file is part of netio230a.
#
# netio230a is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# netio230a is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with netio230a. If not, see <http://www.gnu.org/licenses/>.


 
# example how to use the netio230a class
 
## import the netio230a class:
## for sys.exit(1)
import sys
sys.path.append('e:\\Python')
import netio230a
 
#from datetime import datetime
### for timedelta()
#from datetime import timedelta

import appuifw
import e32


host = "your.dyndns.org"
port = 23
pw = "your chosen password"

appuifw.app.title = u"NETIO 230A"
appuifw.note(u"Welcome to the Koukaam NETIO 230A control.", 'info')

app_lock = e32.Ao_lock()
messagecanvas = appuifw.Text()

try:
    netio = netio230a.netio230a(host, "admin", pw, True, port)
except:
    netio=None
    messagecanvas.set(u"could not connect")


def exit_key_handler():
    app_lock.signal()

def switchPort():
    global netio
    portToChange = appuifw.query(u"Port to switch:", 'number')
    portOn = appuifw.query(u"new status for port %s:"% portToChange, 'number')
    if portToChange == None or portOn == None:
        return
    netio.setPortPower(int(portToChange),bool(int(portOn)))
    updateStatus()

#def subitem1():
#    messagecanvas.set(u'Now first subitem was selected')

def updateStatus():
    global netio
    portPower = netio.getPortList()
    messagecanvas.set( u"" )
    messagecanvas.style = appuifw.STYLE_BOLD
    messagecanvas.add(u"Power Status:\n\n")
    messagecanvas.style = 0
    messagecanvas.add(u"port 1: %s\nport 2: %s\nport 3: %s\nport 4: %s" % (portPower[0],portPower[1],portPower[2],portPower[3] ))

def main():
    global netio
    
    appuifw.app.screen='large'
    appuifw.app.body = messagecanvas
    
    if netio == None:
        # wait 3 seconds:
        e32.ao_sleep(3)
        appuifw.app.set_exit() # this completely closes python
    
    #appuifw.app.menu = [(u"Submenu 1", ((u"sub item 1", subitem1), (u"sub item 2", subitem2))), (u"Exit", exit_key_handler)]
    appuifw.app.menu = [(u"Switch Port", switchPort), (u"Refresh Status", updateStatus), (u"Exit", exit_key_handler)]
    updateStatus()
    
    appuifw.app.exit_key_handler = exit_key_handler

    app_lock.wait()
    netio = None
    
 
if __name__ == '__main__':
    main()

