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

# How to push this file easily to the device (for easier development):
#
#    obexftp.exe -b 00:1f:5d:5b:53:fb -B 11 --chdir /E:/Python/ --put ./example.PyS60.py
#    obexftp.exe -b 00:1f:5d:5b:53:fb -B 11 --chdir /E:/Python/ --put ./accelerometer.py

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


# check what to need here... --------------------------------------------------
import key_codes
### keypress handler trick
import time
# up to here... --------------------------------------------------

KEY_INITIAL_UP_TIME = 0.04
KEY_START_REPEATE_RATE = 0.57
KEY_REPEATE_RATE = 0.15625
# empirically found value on my N95-1 with Python 2.0 on the Python Script Shell by adding the following lines directly after   def cb_select(self):
#        print time.clock() - self.time
#        self.time = time.clock()
#        return


class DeviceController(object):

    def __init__(self, controller, host, username, password, tcp_port):
        self.controller = controller
        self.time = 0
        self.timer = e32.Ao_timer()
        # List items for all listboxes
        self.socket_list = [u"Power Socket 1", u"Power Socket 2", u"Power Socket 3", u"Power Socket 4"]
        # Custom listbox related items, global or within class
        self.list_box = None       # Listbox
        self.e = []          # Entries: list items with icons
        self.icon_on = None   # Icon for selected checkbox
        self.icon_off = None  # Icon for non-selected checkbox
        
        try:
            self.netio = netio230a.netio230a(host, username, password, True, tcp_port)
        except Exception as error:
            self.netio=None
            self.controller.displayUnrecoverableError(u"Connection failed:\n"+str(error))
            return
        configuration.changeConfiguration(configuration.UPDATE, '', host, tcp_port, username, password)
        
        self.power_sockets = self.netio.getPowerSocketList()
        
        if self.netio == None:
            # wait 3 seconds:
            e32.ao_sleep(3)
            #appuifw.app.set_exit() # this completely closes python
            return
        
        #appuifw.app.menu = [(u"Submenu 1", ((u"sub item 1", subitem1), (u"sub item 2", subitem2))), (u"Exit", exit_key_handler)]
        appuifw.app.menu = [(u"Refresh Status", self.update_status), (u"Disconnect", self.disconnect), (u"Exit", self.exit_key_handler)]
        appuifw.app.exit_key_handler = self.exit_key_handler
        self.update_status()

    def disconnect(self):
        self.controller.next_view = 'ChooseDevice'
        self.netio.disconnect()
        self.netio = None
        self.controller.app_lock.signal()

    def exit_key_handler(self):
        self.netio.disconnect()
        self.netio = None
        self.controller.exit_key_handler()
    
    # custom listbox
    # - Checkbox icon for listbox (get_checkbox)
    # - Handle selection on listbox (cb_select)
    # - Handle closing listbox (cb_return)
    # - Initialize and draw listbox (menu_list)
    def get_checkbox(self, a_value):
        ''' Checkbox icon: selected or not '''
        # Create only once, reuse after that
        if not self.icon_on:
            # See avkon2.mbm content (old version)
            # http://alindh.iki.fi/symbian/avkon2.mbm/
            try:
                # webkit checkbox looks better, but might not exist
                self.icon_off = appuifw.Icon(u"z:\\resource\\apps\\webkit.mbm", 12, 31)
                self.icon_on = appuifw.Icon(u"z:\\resource\\apps\\webkit.mbm", 13, 32)
            except:
                # Counting on avkon2 to be there, hopefully with checkbox
                self.icon_off = appuifw.Icon(u"z:\\resource\\apps\\avkon2.mbm", 103, 104)
                self.icon_on = appuifw.Icon(u"z:\\resource\\apps\\avkon2.mbm", 109, 110)
        if a_value:
            return self.icon_on
        else:
            return self.icon_off
     
    def cb_select(self):
        ''' Callback for listbox item selection event '''
        ### keypress handler trick, to allow Enter/Select work
        # fact is: you press the Enter key shortly and this is what happens:
        #   callback called once immediately and once again after ~ 0.04 s
        # when you press the button for a longer period this is what happens:
        #   callback called once immediately and once again after ~ 0.04 s then after ~ 0.56 s it is called every 0.15 s
        #self.timer.cancel()
        # Ignore first (button down) and non-timer triggered (button up) events
        if (not self.time): # or (time.clock() - self.time < KEY_REPEATE_RATE * .7):
            self.time = time.clock()
            # Should be more than start keyrepeat rate
            #self.timer.after(KEY_START_REPEATE_RATE * 1.25, self.cb_select)
            return
        if time.clock() - self.time > KEY_INITIAL_UP_TIME * 2:
            self.time = 0
            return
        self.time = 0
        ### keypress handler trick, done
     
        # Current listbox selection
        index = self.list_box.current()
     
        # Change selected item icon: on <-> off
        if self.e[index][1] == self.icon_on:
            new_icon = self.icon_off
            power_socket_on = False
        else:
            new_icon = self.icon_on
            power_socket_on = True
        self.netio.setPowerSocketPower(index+1,power_socket_on)
        self.power_sockets[index] = power_socket_on
        
        self.e[index] = (self.e[index][0], new_icon)
     
        # Show new list, same item selected
        self.list_box.set_list(self.e, index)
        appuifw.app.body = self.list_box
     
        # Make it visible
        e32.ao_yield()
    
    def menu_list(self):
        ''' Custom multi-selection listbox '''
        self.e = []
        # Mark initial selections
        for item in range(len(self.socket_list)):
            if self.power_sockets[item] == True:
                icon = self.get_checkbox(True)
            else:
                icon = self.get_checkbox(False)
            self.e.append((self.socket_list[item], icon))
        
        self.list_box = appuifw.Listbox(self.e, self.cb_select)
        appuifw.app.body = self.list_box
        
        # Several ways to select item
        # BUG: One press of Enter/Select gives two events: KeyDown and KeyUp
        # BUG: ...or even 3+ with key repeat
        # Fix: write own key handler, react only on KeyUp event
        # Fix: use timer to separate "one" key press
        self.list_box.bind(key_codes.EKeyRightArrow, self.cb_select)
        self.list_box.bind(key_codes.EKeyEnter, self.cb_select)
        self.list_box.bind(key_codes.EKeySelect, self.cb_select)

    def update_status(self):
        self.power_sockets = self.netio.getPowerSocketList()
        self.menu_list()

class ChooseDevice(object):
    def __init__(self, controller):
        self.controller = controller
        about = appuifw.Text()
        about.set(u"Control your Koukaam NETIO-230A with this software for Symbian S60 phones.")
        appuifw.app.body = about
        about.focus = False

    def get_device(self):
        # devices from configuration has the form [devicename, host, tcp_port, username, password]
        devices = configuration.getConfiguration()
        if len(devices)>0 and appuifw.query(u"Choose a previously used device?", "query"):
            # define the list of items
            L = []
            for device in devices:
                name = device[0]
                host = device[1]
                L.append(unicode(host if name == '' else "%s - %s" % (name, host)))
            # create the selection list
            index = appuifw.popup_menu(L, u"Previously connected")
            if index is None:
                return -1
            return devices[index]
        else:
            # define the field list (consists of tuples: (label, type ,value)); label is a unicode string
            # type is one of the following strings: 'text', 'number', 'date', 'time',or 'combo'
            # see <http://gist.github.com/322309#file_form.py>
            data = [(u'Hostname/IP','text', u''),(u'TCP Port','number', 1234),(u'Username','text',u'admin')]
            # set the view/edit mode of the form  
            flags = appuifw.FFormEditModeOnly
            # creates the form
            f = appuifw.Form(data, flags)
            f.save_hook = self.save_input
            # make the form visible on the UI
            f.execute()
            self.host = f[0][2]
            self.tcp_port = f[1][2]
            self.username = f[2][2]
            password = appuifw.query(u"Password",'code')
            return ['', self.host, self.tcp_port, self.username, password]
    
    def save_input(self, arg):
        self.saved = True
        return True

class Controller:
    def __init__(self):
        appuifw.app.title = u"NETIO-230A"
        #appuifw.note(u"Welcome to the Koukaam NETIO-230A control.", 'info')
        #appuifw.app.screen='large'
        appuifw.app.exit_key_handler = self.exit_key_handler
        self.app_lock = e32.Ao_lock()
        self.apo = ''
        self.next_view = 'ChooseDevice'
    
    def run(self):
        device = ''
        while self.next_view != '':
            if self.next_view == 'ChooseDevice':
                self.next_view = ''
                cd = ChooseDevice(self)
                device = cd.get_device()
                if type(device) != list:
                    return
                self.next_view = 'DeviceController'
            
            if self.next_view == 'DeviceController':
                self.next_view = ''
                self.select_access_point()
                host, username, password, tcp_port = device[1], device[3], device[4], device[2]
                dc = DeviceController(self, host, username, password, tcp_port)
                self.app_lock.wait()

    def connected(self):
        if type(self.apo) == 'string':
            return False
        try:
            return self.apo.ip()
        except:
            return False

    def select_access_point(self):
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
        
        self.apo = socket.access_point(aps[item]['iapid'])
        socket.set_default_access_point(self.apo)
        
        return True
    
    def exit_key_handler(self):
        try:
            self.apo.stop()
        except Exception as error:
            print "could not stop access point: " + str(error)
        self.app_lock.signal()

    def displayUnrecoverableError(self, message):
        messagecanvas = appuifw.Text()
        messagecanvas.set(unicode(message))
        appuifw.app.body = messagecanvas


def main():
    control = Controller()
    control.run()

if __name__ == '__main__':
    main()

