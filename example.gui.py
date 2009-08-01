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
import gtk
## for debugging (set debug mark with pdb.set_trace() )
import pdb
import netio230a

host = "192.168.1.2"
pw = "your choosen password"
  
class netio230aGUI:
    
    
    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file("netio230aGUI.glade") 
        
        self.window = builder.get_object("mainWindow")
        self.about_dialog = builder.get_object( "aboutDialog" )
        
        builder.connect_signals(self)
        
        self.__update_output()
    
    def gtk_main_quit( self, window ):
        gtk.main_quit()
    
    def on_window_destroy(self, widget, data=None):
        gtk.main_quit()
    
    def cb_about(self, button):
        self.about_dialog.run()
        self.about_dialog.hide()
        
    def cb_updateToggleButtons(self, notebook, page, page_num):
        if page_num != 2:
            return
        try:
            netio = netio230a.netio230a(host, "admin", pw, True)
        except StandardError:
            print("could not connect")
            return
        ports = netio.getAllPorts()
        netio = None
        self.window.get_children()[0].get_children()[2].get_children()[0].get_children()[1].set_active(ports[0].getPowerOn())
        self.window.get_children()[0].get_children()[2].get_children()[1].get_children()[1].set_active(ports[1].getPowerOn())
        self.window.get_children()[0].get_children()[2].get_children()[2].get_children()[1].set_active(ports[2].getPowerOn())
        self.window.get_children()[0].get_children()[2].get_children()[3].get_children()[1].set_active(ports[3].getPowerOn())
    
    def cb_refresh(self, button):
        self.__update_output()

    def __update_output(self):
        try:
            netio = netio230a.netio230a(host, "admin", pw, True)
        except StandardError:
            print("could not connect")
            return
        ports = netio.getAllPorts()
        netio = None
        tb = gtk.TextBuffer()
        tb.set_text("power status:\nport 1: %s\nport 2: %s\nport 3: %s\nport 4: %s" % (ports[0].getPowerOn(),ports[1].getPowerOn(),ports[2].getPowerOn(),ports[3].getPowerOn()))
        self.window.get_children()[0].get_children()[0].get_children()[1].set_buffer( tb )
    
        
    def cb_switch1On(self, togglebutton):
        self.__setPort(1,togglebutton.get_active())
    
    def cb_switch2On(self, togglebutton):
        self.__setPort(2,togglebutton.get_active())
    
    def cb_switch3On(self, togglebutton):
        self.__setPort(3,togglebutton.get_active())
    
    def cb_switch4On(self, togglebutton):
        self.__setPort(4,togglebutton.get_active())
    
    def __setPort(self,portNr,portOn=True):
        try:
            netio = netio230a.netio230a(host, "admin", pw, True)
        except StandardError:
            print("could not connect")
            return
        netio.setPortPower(portNr,portOn)
        netio = None
    
    
    
if __name__ == "__main__":
    gui = netio230aGUI()
    gui.window.show()
    gtk.main()

