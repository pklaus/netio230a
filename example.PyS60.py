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


# -------------------------------       ABOUT       ----------------------------------- 
# This is a program written for the Python for
# S60 platform (Nokia Symbian mobile phones).
# It is tested on a Nokia N95.
# -----------------------------       DEPENDENCIES      -------------------------------
# please do not use any old version of python...
# use 1.9.x or later found on <https://garage.maemo.org/frs/?group_id=854>
# -------------------------------------------------------------------------------------


import sys
sys.path.append('e:\\Python')
import netio230a
import configuration

try:
    # http://discussion.forum.nokia.com/forum/showthread.php?p=575213
    # Try to import 'btsocket' as 'socket' (just for 1.9.x)
    sys.modules['socket'] = __import__('btsocket')
except ImportError:
    pass
# for the raw TCP socket connection:
import socket

import appuifw
import e32


class DeviceController(object):

    def __init__(self, messagecanvas, host, username, password, tcp_port):
        self.messagecanvas = messagecanvas
        
        try:
            self.netio = netio230a.netio230a(host, username, password, True, tcp_port)
        except:
            self.netio=None
            self.messagecanvas.set(u"could not connect")
            return
        configuration.changeConfiguration(configuration.UPDATE, '', host, tcp_port, username, password)
        
        if self.netio == None:
            # wait 3 seconds:
            e32.ao_sleep(3)
            #appuifw.app.set_exit() # this completely closes python
            return
        
        #appuifw.app.menu = [(u"Submenu 1", ((u"sub item 1", subitem1), (u"sub item 2", subitem2))), (u"Exit", exit_key_handler)]
        appuifw.app.menu = [(u"Switch Power Socket", self.switch_power_socket), (u"Refresh Status", self.update_status), (u"Exit", exit_key_handler)]
        appuifw.app.exit_key_handler = exit_key_handler
        self.update_status()


    def switch_power_socket(self):
        power_socket_to_change = 0
        while int(power_socket_to_change) < 1 or power_socket_to_change > 4:
            power_socket_to_change = appuifw.query(u"Power socket to switch (between 1 and 4):", 'number')
            if power_socket_to_change == None:
                return
        states = [u"On", u"Off"]
        state = appuifw.popup_menu(states, u"new status for power socket %s:"% power_socket_to_change)
        if power_socket_to_change == None or state == None:
            return
        if state == 1:
            power_socket_on = False
        elif state == 0:
            power_socket_on = True
        self.netio.setPowerSocketPower(int(power_socket_to_change),power_socket_on)
        self.update_status()

    #def subitem1():
    #    self.messagecanvas.set(u'Now first subitem was selected')

    def update_status(self):
        power_sockets = self.netio.getPowerSocketList()
        self.messagecanvas.set( u"" )
        self.messagecanvas.style = appuifw.STYLE_BOLD
        self.messagecanvas.add(u"Power Status:\n\n")
        self.messagecanvas.style = 0
        self.messagecanvas.add(u"port 1: %s\nport 2: %s\nport 3: %s\nport 4: %s" % (power_sockets[0],power_sockets[1],power_sockets[2],power_sockets[3] ))

class ChooseDevice(object):
    def __init__(self, messagecanvas):
        self.messagecanvas = messagecanvas

    def get_device(self):
        # devices from configuration has the form [devicename, host, tcp_port, username, password]
        devices = configuration.getConfiguration()
        if len(devices)>0 and appuifw.query(u"Choose a previously used device?:", "query"):
            # define the list of items
            L = []
            for device in devices:
                name = device[0]
                host = device[1]
                L.append(unicode(host if name == '' else "%s - %s" % (name, host)))
            # create the selection list
            index = appuifw.popup_menu(L, u"Previously connected:")
            if index is None:
                return -1
            return devices[index]
        else:
            tcp_port = ""
            while tcp_port <= 0 or tcp_port > 32000:
                host,tcp_port = appuifw.multi_query(u"Hostname/IP:",u"TCP Port:")
                try:
                    tcp_port = int(tcp_port)
                except:
                    tcp_port = 0
            username, password = appuifw.multi_query(u"Username:",u"Password:")
            return ['',host,tcp_port, username, password]

apo = ""
def select_access_point():
    """ Select the default access point.
        Return True if the selection was done or False if not
        found on <http://croozeus.com/blogs/?p=836>
    """
    aps = socket.access_points()
    if not aps:
        appuifw.note(u"No access points available","error")
        return False
    ap_labels = map(lambda x: x['name'], aps)
    item = appuifw.popup_menu(ap_labels,u"Access points:")
    if item is None:
        return False
    
    global apo
    apo = socket.access_point(aps[item]['iapid'])
    socket.set_default_access_point(apo)
    
    return True

def exit_key_handler():
    global apo
    try:
        apo.stop()
    except:
        pass
    global app_lock
    app_lock.signal()

app_lock = e32.Ao_lock()
def main():
    global app_lock
    
    appuifw.app.title = u"NETIO 230A"
    appuifw.note(u"Welcome to the Koukaam NETIO-230A control.", 'info')

    messagecanvas = appuifw.Text()
    
    appuifw.app.screen='large'
    appuifw.app.body = messagecanvas
    
    appuifw.app.exit_key_handler = exit_key_handler
    
    cd = ChooseDevice(messagecanvas)
    device = cd.get_device()
    if type(device) != list:
        return
    
    select_access_point()
    host, username, password, tcp_port = device[1], device[3], device[4], device[2]
    dc = DeviceController(messagecanvas, host, username, password, tcp_port)
    
    app_lock.wait()

if __name__ == '__main__':
    main()

