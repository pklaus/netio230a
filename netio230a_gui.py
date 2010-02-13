#!/usr/bin/env python
# -*- encoding: UTF8 -*-

# author: Philipp Klaus, philipp.l.klaus AT web.de


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


# documentation on PyGTK:
# http://library.gnome.org/devel/pygtk/stable/
# http://library.gnome.org/devel/pygobject/stable/

import sys
import os # for os.path.abspath() and os.path.dirname()
import gtk
## for debugging (set debug mark with pdb.set_trace() )
import pdb
import netio230a

host = "192.168.1.2"
tcp_port = 1234
username = "admin"
pw = "your choosen password"
  
class netio230aGUI:
    
    
    def __init__(self):
        fullpath = os.path.abspath(os.path.dirname(sys.argv[0]))
        builder = gtk.Builder()
        builder.add_from_file(fullpath + "/resources/netio230aGUI.glade") 
        
        self.window = builder.get_object("mainWindow")
        self.about_dialog = builder.get_object( "aboutDialog" )
        
        builder.connect_signals(self)
        
        self.__updatePowerSocketStatus()
    
    def gtk_main_quit( self, window ):
        gtk.main_quit()
    
    def on_window_destroy(self, widget, data=None):
        gtk.main_quit()
    
    def cb_about(self, button):
        self.about_dialog.run()
        self.about_dialog.hide()
        
    def cb_updateDisplay(self, notebook, page, page_num):
        if page_num == 0:
            self.__updatePowerSocketStatus()
        elif page_num == 1:
            self.__updateSystemSetup()
        elif page_num == 2:
            try:
                netio = netio230a.netio230a(host, username, pw, True, tcp_port)
            except StandardError:
                print("could not connect")
                return
            power_sockets = netio.getAllPowerSockets()
            netio = None
            self.window.get_children()[0].get_children()[1].get_children()[2].get_children()[0].get_children()[1].set_active(power_sockets[0].getPowerOn())
            self.window.get_children()[0].get_children()[1].get_children()[2].get_children()[1].get_children()[1].set_active(power_sockets[1].getPowerOn())
            self.window.get_children()[0].get_children()[1].get_children()[2].get_children()[2].get_children()[1].set_active(power_sockets[2].getPowerOn())
            self.window.get_children()[0].get_children()[1].get_children()[2].get_children()[3].get_children()[1].set_active(power_sockets[3].getPowerOn())
        else:
            return
    
    def cb_refresh(self, button):
        self.__updatePowerSocketStatus()

    def __updatePowerSocketStatus(self):
        try:
            netio = netio230a.netio230a(host, username, pw, True, tcp_port)
        except StandardError:
            print("could not connect")
            return
        power_sockets = netio.getAllPowerSockets()
        netio = None
        tb = gtk.TextBuffer()
        tb.set_text("power status:\nsocket 1: %s\nsocket 2: %s\nsocket 3: %s\nsocket 4: %s" % (power_sockets[0].getPowerOn(),power_sockets[1].getPowerOn(),power_sockets[2].getPowerOn(),power_sockets[3].getPowerOn()))
        self.window.get_children()[0].get_children()[1].get_children()[0].get_children()[1].set_buffer( tb )
    
    
    
    def __updateSystemSetup(self):
        try:
            netio = netio230a.netio230a(host, username, pw, True, tcp_port)
        except StandardError:
            print("could not connect")
            return
        deviceAlias = netio.getDeviceAlias()
        version = netio.getFirmwareVersion()
        systemTime = netio.getSystemTime().isoformat(" ")
        timezoneOffset = netio.getSystemTimezone()
        sntpSettings = netio.getSntpSettings()
        netio = None
        self.window.get_children()[0].get_children()[1].get_children()[1].get_children()[0].get_children()[1].set_text( deviceAlias )
        self.window.get_children()[0].get_children()[1].get_children()[1].get_children()[1].get_children()[1].set_text( version )
        self.window.get_children()[0].get_children()[1].get_children()[1].get_children()[2].get_children()[1].set_text( systemTime )
        self.window.get_children()[0].get_children()[1].get_children()[1].get_children()[3].get_children()[1].set_text( str(timezoneOffset) + " hours" )
        self.window.get_children()[0].get_children()[1].get_children()[1].get_children()[4].get_children()[1].set_text( sntpSettings )
    
        
    def cb_switch1On(self, togglebutton):
        self.__setPowerSocket(1,togglebutton.get_active())
    
    def cb_switch2On(self, togglebutton):
        self.__setPowerSocket(2,togglebutton.get_active())
    
    def cb_switch3On(self, togglebutton):
        self.__setPowerSocket(3,togglebutton.get_active())
    
    def cb_switch4On(self, togglebutton):
        self.__setPowerSocket(4,togglebutton.get_active())
    
    def __setPowerSocket(self,socket_nr,socket_power=True):
        try:
            netio = netio230a.netio230a(host, username, pw, True, tcp_port)
        except StandardError:
            print("could not connect")
            return
        netio.setPowerSocketPower(socket_nr,socket_power)
        netio = None
    
    
    
if __name__ == "__main__":
    gui = netio230aGUI()
    gui.window.show()
    gtk.main()

