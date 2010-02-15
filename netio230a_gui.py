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
#
# good pygtk tutorial: <http://zetcode.com/tutorials/pygtktutorial/>

import sys
import os # for os.path.abspath() and os.path.dirname()
import gtk
## for debugging (set debug mark with pdb.set_trace() )
import pdb
import netio230a


PROGRAM_ICON = 'netio230a_icon.png'
DEVICE_CONTROLLER_UI = "netio230aGUI.glade"
CONNECTION_DETAIL_UI = "netio230aGUI_dialog.glade"

def getAbsoluteFilepath(filename):
    fullpath = os.path.abspath(os.path.dirname(sys.argv[0]))
    return fullpath + '/resources/' + filename

class DeviceController:
    def __init__(self,controller,connection_details):
        self.controller = controller
    
        self.__host = connection_details['host']
        self.__tcp_port = connection_details['tcp_port']
        self.__username = connection_details['username']
        self.__pw = connection_details['password']
        try:
            self.netio = netio230a.netio230a(self.__host, self.__username, self.__pw, True, self.__tcp_port)
        except StandardError, error:
            print str(error)
        
        self.builder = gtk.Builder()
        self.builder.add_from_file(getAbsoluteFilepath(DEVICE_CONTROLLER_UI))
        
        self.window = self.builder.get_object("mainWindow")
        self.about_dialog = self.builder.get_object( "aboutDialog" )
        
        
        self.__updateLabels()
        self.__updatePowerSocketStatus()
        self.builder.connect_signals(self)
        self.window.show()
    
    def cb_disconnect(self, button, *args):
        self.controller.setNextStep("runDeviceSelector")
        gtk.main_quit()
        self.window.hide()
        return False
    
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
                power_sockets = self.netio.getAllPowerSockets()
            except StandardError, error:
                print(str(error))
                return
            
            netio = None
            for i in range(4):
                ## shorter form with builder.get_object(). cf. <http://stackoverflow.com/questions/2072976/access-to-widget-in-gtk>
                self.builder.get_object("socket"+str(i+1)).set_active(power_sockets[i].getPowerOn())
        else:
            return
    
    def cb_refresh(self, button):
        self.__updatePowerSocketStatus()

    def __updatePowerSocketStatus(self):
        try:
            power_sockets = self.netio.getAllPowerSockets()
        except StandardError, error:
            print(str(error))
            return
        self.netio.disconnect()
        tb = gtk.TextBuffer()
        tb.set_text("power status:\nsocket 1: %s\nsocket 2: %s\nsocket 3: %s\nsocket 4: %s" % (power_sockets[0].getPowerOn(),power_sockets[1].getPowerOn(),power_sockets[2].getPowerOn(),power_sockets[3].getPowerOn()))
        self.builder.get_object("status_output").set_buffer( tb )
    
    def __updateLabels(self):
        try:
            power_sockets = self.netio.getAllPowerSockets()
        except StandardError, error:
            print(str(error))
            return
        self.netio.disconnect()
        for i in range(4):
            label_name = "socket"+str(i+1)+"_label"
            self.builder.get_object(label_name).set_text(self.builder.get_object(label_name).get_text()+' ("'+power_sockets[i].getName()+'")')
    
    
    
    def __updateSystemSetup(self):
        try:
            deviceAlias = self.netio.getDeviceAlias()
            version = self.netio.getFirmwareVersion()
            systemTime = self.netio.getSystemTime().isoformat(" ")
            timezoneOffset = self.netio.getSystemTimezone()
            sntpSettings = self.netio.getSntpSettings()
        except StandardError, error:
            print(str(error))
            return
        self.netio.disconnect()
        self.builder.get_object("device_name").set_text( deviceAlias )
        self.builder.get_object("firmware_version").set_text( version )
        self.builder.get_object("system_time").set_text( systemTime )
        self.builder.get_object("timezone_offset").set_text( str(timezoneOffset) + " hours" )
        self.builder.get_object("sntp_settings").set_text( sntpSettings )
    
        
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
            self.netio.setPowerSocketPower(socket_nr,socket_power)
        except StandardError, error:
            print(str(error))
        self.netio.disconnect()

class ConnectionDetailDialog:
    def __init__(self,host='',username='admin',password='',port=1234):
        self.builder = gtk.Builder()
        self.builder.add_from_file(getAbsoluteFilepath(CONNECTION_DETAIL_UI))
        self.dialog = self.builder.get_object("ConnectionDetailDialog")
        # pre-fill values of text entries
        self.builder.get_object("host_text").set_text(host)
        self.builder.get_object("port_text").set_text(str(port))
        self.builder.get_object("username_text").set_text(username)
        self.builder.get_object("password_text").set_text(password)
        # focus the first empty text entry:
        entry_field_names = ['host','port','username','password']
        for field_name in entry_field_names:
            if str(locals()[field_name]) == '': # this is nice trick to call the variable with the name stored in field_name
                self.builder.get_object(field_name+"_text").grab_focus()
                break
        self.builder.get_object("action_area").set_focus_chain([self.builder.get_object("connect_button"), self.builder.get_object("abort_button")])
    
    def run(self):
        self.builder.connect_signals(self)
        return self.dialog.run()
    
    def updateData(self):
        self.__host = self.builder.get_object("host_text").get_text()
        self.__username = self.builder.get_object("username_text").get_text()
        self.__pw = self.builder.get_object("password_text").get_text()
        try:
            self.__tcp_port = int(self.builder.get_object("port_text").get_text())
        except:
            self.__tcp_port = 0
            self.builder.get_object("port_text").set_text("0")
    
    def enter_pressed(self, widget):
        self.builder.get_object("connect_button").activate()
        ## could also be done by setting the default response id:
        #self.dialog.set_default_response(response_id) # resp_id might be 1
    
    def response_handler(self, widget, response_id):
        self.updateData()
    
    def getData(self):
        data = dict()
        data['host'] = self.__host
        data['username'] = self.__username
        data['password'] = self.__pw
        data['tcp_port'] = self.__tcp_port
        return data
        

class DeviceSelector:
    # close the window and quit
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()

    def __init__(self, controller):
        self.controller = controller
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Select a Device")
        self.window.set_icon_from_file(getAbsoluteFilepath(PROGRAM_ICON))

        self.window.set_size_request(320, 150)
        self.window.connect("delete_event", self.delete_event)

        # create a TreeStore with two string columns to use as the model
        self.treestore = gtk.TreeStore(str,str)

        devices = netio230a.get_all_detected_devices()
        piter = self.treestore.append(None,['auto-detected devices',''])
        for device in devices:
            self.treestore.append(piter,[device[0],str(device[1][0])+'.'+str(device[1][1])+'.'+str(device[1][2])+'.'+str(device[1][3])])
        
        # more on TreeViews: <http://www.thesatya.com/blog/2007/10/pygtk_treeview.html>
        # and <http://www.pygtk.org/pygtk2tutorial/ch-TreeViewWidget.html#sec-TreeViewOverview>
        # create the TreeView using treestore
        self.treeview = gtk.TreeView(self.treestore)
        # create the TreeViewColumn to display the data
        self.tvcolumn = gtk.TreeViewColumn('Device Name')
        self.tvcolumn1 = gtk.TreeViewColumn('IP Address')
        # add tvcolumn to treeview
        self.treeview.append_column(self.tvcolumn)
        self.treeview.append_column(self.tvcolumn1)
        # create a CellRendererText to render the data
        self.cell = gtk.CellRendererText()
        # add the cell to the tvcolumn and allow it to expand
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn1.pack_start(self.cell, True)
        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.tvcolumn1.add_attribute(self.cell, 'text', 1)
        # make it searchable
        self.treeview.set_search_column(0)
        # Allow sorting on the column
        self.tvcolumn.set_sort_column_id(0)
        self.tvcolumn1.set_sort_column_id(1)
        # Allow drag and drop reordering of rows
        self.treeview.set_reorderable(True)
        self.treeview.expand_all()
        self.treeview.set_size_request(-1,200)

        spacing, homogeneous, expand, fill, padding = 2, False, True, True, 2
        # Create a new hbox with the appropriate homogeneous
        # and spacing settings
        box = gtk.HBox(homogeneous, spacing)
        
        # create the buttons
        button = gtk.Button("other device")
        box.pack_start(button, expand, fill, padding)
        button.connect("clicked",self.connect_clicked)
        button = gtk.Button("connect")
        box.pack_start(button, expand, fill, padding)
        button.connect("clicked",self.connect_clicked, self.treeview)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC);
        scroll.add(self.treeview);

        spacing, homogenious, expand, fill, padding = 1, False, False, True, 2
        superbox = gtk.VBox(homogeneous, spacing)
        superbox.pack_start(scroll, True, True, 1)
        superbox.pack_start(box, False, False, 0)
        
        self.superbox = superbox
        
        self.window.add(self.superbox)
        self.window.show_all()
        
    def connect_clicked(self, button, *args):
        host = ''
        for arg in args:
            if type(arg)==gtk.TreeView:
                (model, treeiter) = arg.get_selection().get_selected()
                host = model.get_value(treeiter,1)
                
                #dlg = gtk.Dialog(title='Ein Dialog',
                #    parent=self.window,
                #    buttons=(gtk.STOCK_CANCEL,
                #             gtk.RESPONSE_REJECT,
                #             gtk.STOCK_OK,
                #             gtk.RESPONSE_OK))
                #result = dlg.run()
                #if result == gtk.RESPONSE_OK:
                #    print 'Mach mal!'
                #else:
                #    print 'Lieber nicht.'
                #dlg.destroy()
        dl = ConnectionDetailDialog(host)
        result = dl.run()
        while result == 1:
            data = dl.getData()
            try:
                netio = netio230a.netio230a(data['host'], data['username'], data['password'], True, data['tcp_port'])
                netio = None
                break
            except StandardError, error:
                netio = None
                continue_abort = gtk.MessageDialog(parent=dl.dialog, flags=gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK_CANCEL, message_format="Connection failed. \n\n"+str(error)+"\n\nChange connection details and try again?")
                response = continue_abort.run()
                continue_abort.destroy()
                if response == gtk.RESPONSE_OK:
                    result = dl.run()
                else:
                    result = 0
                    break
        
        dl.dialog.hide()
        del dl
        if result != 1:
            return
        
        self.controller.setNextStep("runDeviceController", host = data['host'], tcp_port = data['tcp_port'], username=data['username'], password = data['password'])
        #self.window.hide()
        self.window.destroy()
        gtk.main_quit()
        return False

class TrayIcon(gtk.StatusIcon):
    # reely adapted from the tracker-applet: <https://labs.codethink.co.uk/index.php/p/tracker/source/tree/master/python/applet/applet.py>
    def __init__(self,controller):
        gtk.StatusIcon.__init__(self)
        menu = '''
            <ui>
             <menubar name="Menubar">
              <menu action="Menu">
               <menuitem action="Socket1"/>
               <menuitem action="Socket2"/>
               <menuitem action="Socket3"/>
               <menuitem action="Socket4"/>
               <menuitem action="Preferences"/>
               <separator/>
               <menuitem action="About"/>
              </menu>
             </menubar>
            </ui>
        '''
        actions = [
            ('Menu',  None, 'Menu'),
            #('Search', None, '_Search...', None, 'Search files with MetaTracker', self.on_activate),
            ('Socket1', gtk.STOCK_PREFERENCES, 'Toggle Socket _1', None, 'Switch power socket 1 on or off.', self.on_toggle),
            ('Socket2', gtk.STOCK_PREFERENCES, 'Toggle Socket _2', None, 'Switch power socket 2 on or off.', self.on_toggle),
            ('Socket3', gtk.STOCK_PREFERENCES, 'Toggle Socket _3', None, 'Switch power socket 3 on or off.', self.on_toggle),
            ('Socket4', gtk.STOCK_PREFERENCES, 'Toggle Socket _4', None, 'Switch power socket 4 on or off.', self.on_toggle),
            ('Preferences', gtk.STOCK_PREFERENCES, '_Preferences...', None, 'Change MetaTracker preferences', self.on_preferences),
            ('About', gtk.STOCK_ABOUT, '_About...', None, 'About NETIO-230A control', self.on_about)]
        ag = gtk.ActionGroup('Actions')
        ag.add_actions(actions)
        self.controller = controller
        self.manager = gtk.UIManager()
        self.manager.insert_action_group(ag, 0)
        self.manager.add_ui_from_string(menu)
        self.menu = self.manager.get_widget('/Menubar/Menu/About').props.parent
        search = self.manager.get_widget('/Menubar/Menu/Search')
        #search.get_children()[0].set_markup('<b>_Search...</b>')
        #search.get_children()[0].set_use_underline(True)
        #search.get_children()[0].set_use_markup(True)
        #search.get_children()[1].set_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU)
        self.set_from_file(getAbsoluteFilepath(PROGRAM_ICON))
        self.set_tooltip('NETIO-230A control')
        self.set_visible(True)
        self.connect('activate', self.on_activate)
        self.connect('popup-menu', self.on_popup_menu)

    def on_activate(self, data):
        print("ok, here we want to toggle the visibility of the program...")
    
    def on_toggle(self, action):
        try:
            socket_name = action.get_name()
        except:
            raise NameError("actions seems to be no gtk.Action! something went wrong")
        if socket_name.find("Socket") != -1:
            try:
                print("toggeling " + socket_name[6])
                print self.controller.topical_window.netio.togglePowerSocketPower(int(socket_name[6]))
                self.controller.topical_window.netio.disconnect()
            except:
                print("sorry, log in first.")

    def on_popup_menu(self, status, button, time):
        self.menu.popup(None, None, None, button, time)

    def on_preferences(self, data):
        print 'preferences'

    def on_about(self, data):
        dialog = gtk.AboutDialog()
        dialog.set_name('NETIO-230A control')
        dialog.set_version('0.1')
        dialog.set_comments('Command the NETIO-230A device')
        dialog.set_website('http://pklaus.github.com/netio230a')
        dialog.run()
        dialog.destroy()



class Controller(object):
    def run(self):
        self.nextStep = "runDeviceSelector"
        icon = TrayIcon(self)
        while self.nextStep != "":
            if self.nextStep == "runDeviceSelector":
                self.nextStep = ""
                self.runDeviceSelector()
            elif self.nextStep == "runDeviceController":
                self.nextStep = ""
                self.runDeviceController(self.nextStepKWArgs)
    
    def setNextStep(self,what, **kwargs):
        self.nextStep = what
        self.nextStepKWArgs = kwargs
    
    def runDeviceSelector(self):
        self.topical_window = DeviceSelector(self)
        gtk.main()
    
    def runDeviceController(self, connection_details):
        self.topical_window = DeviceController(self, connection_details)
        gtk.main()


def main():
    controller = Controller()
    controller.run()

if __name__ == "__main__":
    main()

