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
# to store and retrieve recent connections:
import configuration

import gobject # for the timer
import signal # for [Ctrl]-[c] catching

PROGRAM_ICON = 'netio230a_icon.png'
DEVICE_CONTROLLER_UI = "netio230aGUI.glade"
CONNECTION_DETAIL_UI = "netio230aGUI_dialog.glade"

AUTO_UPDATE = 3 # auto update time seconds

OVERWRITE_TELNET_SOCKET_TIMEOUT = 1


DEBUG_MODE = True
MIN_DEBUG_LEVEL = 7


# constants do not touch:
DBG_WARNING = 8


# remember position of window:
#    (x, y) = w.get_position()
#    (w, h) = w.get_size()
#
#restore position:
#    w = gtk.Window()
#    w.move(x, y)
#    w.resize(w, h)


def getAbsoluteFilepath(filename):
    fullpath = os.path.abspath(os.path.dirname(sys.argv[0]))
    return fullpath + '/resources/' + filename

class AboutDialog:
    def __init__(self):
        
        self.builder = gtk.Builder()
        self.builder.add_from_file(getAbsoluteFilepath(DEVICE_CONTROLLER_UI))
        
        self.about_dialog = self.builder.get_object( "aboutDialog" )
        self.about_dialog.set_icon_from_file(getAbsoluteFilepath(PROGRAM_ICON))
    
    def run(self):
        self.about_dialog.run()
        self.about_dialog.destroy()

class DeviceController:
    def __init__(self,controller,connection_details):
        self.controller = controller
    
        self.__host = connection_details['host']
        self.__tcp_port = connection_details['tcp_port']
        self.__username = connection_details['username']
        self.__pw = connection_details['password']
        try:
            self.netio = netio230a.netio230a(self.__host, self.__username, self.__pw, True, self.__tcp_port)
            self.netio.enable_logging(open(configuration.LOG_FILE,'w'))
        except StandardError, error:
            print(str(error))
        
        self.builder = gtk.Builder()
        self.builder.add_from_file(getAbsoluteFilepath(DEVICE_CONTROLLER_UI))
        
        self.window = self.builder.get_object("mainWindow")
        self.window.set_icon_from_file(getAbsoluteFilepath(PROGRAM_ICON))
        self.builder.get_object("link_button").set_uri('http://'+self.__host)
        
        self.updateLabels()
        self.updatePowerSocketStatus()
        self.builder.connect_signals(self)
        self.window.connect("window-state-event",self.handle_window_state_events)
        self.window.show()
        
        # a timer to update the UI automatically
        self.timer_id = gobject.timeout_add(1000, self.timer_tick) # use gobject.timeout_add_seconds() for longer periods
        self.timer_continue = True
        self.counter = 0
    
    
    def timer_tick(self):
        if self.timer_id is not None and self.timer_continue:
            self.counter += 1
            if self.counter%AUTO_UPDATE == 0:
                try:
                    self.updatePowerSocketStatus()
                except StandardError, error:
                    pass
                    debug("The updatePowerSocketStatus action triggered by the timer failed: " + str(error), DBG_WARNING)
                self.counter = 0
            return True # run again in one second
        return False # stop running again
    
    def handle_window_state_events(self, window, event):
        if event.changed_mask & gtk.gdk.WINDOW_STATE_ICONIFIED:
            if event.new_window_state & gtk.gdk.WINDOW_STATE_ICONIFIED:
                #print 'Window was minimized!'
                self.controller.toggle_visibility()
            #else:
            #    print 'Window was unminimized!'
    
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
        about = AboutDialog()
        about.run()
        
    def cb_updateDisplay(self, notebook, page, page_num):
        self.updateStatusBar()
        if page_num == 0:
            self.updatePowerSocketStatus()
        elif page_num == 1:
            self.updateSystemSetup()
            pass
        elif page_num == 2:
            self.updatePowerSocketStatus()
        else:
            return
    
    def cb_refresh(self, button):
        self.updatePowerSocketStatus()

    def updatePowerSocketStatus(self):
        try:
            power_sockets = self.netio.getAllPowerSockets()
        except StandardError, error:
            print(str(error))
            return
        #self.netio.disconnect()
        
        # update checkboxes on this GUI and on the status icon:
        i = 1
        new_status = []
        for power_socket in power_sockets:
            ## shorter form with builder.get_object(). cf. <http://stackoverflow.com/questions/2072976/access-to-widget-in-gtk>
            self.builder.get_object("socket"+str(i)).set_active(power_socket.getPowerOn())
            new_status.append([power_socket.getName(),power_socket.getPowerOn()])
            i += 1
        self.controller.icon.update_checkboxes(new_status)
        
        # update the status text:
        tb = gtk.TextBuffer()
        tb.set_text("power status:\nsocket 1: %s\nsocket 2: %s\nsocket 3: %s\nsocket 4: %s" % (power_sockets[0].getPowerOn(),power_sockets[1].getPowerOn(),power_sockets[2].getPowerOn(),power_sockets[3].getPowerOn()))
        self.builder.get_object("status_output").set_buffer( tb )
        self.updateStatusBar()

    def updateStatusBar(self):
        self.builder.get_object("status_label").set_text(u"ø %.1f ms/request (%d total)" % (self.netio.mean_request_time*1000, self.netio.number_of_sent_requests))
    
    def updateLabels(self):
        try:
            power_sockets = self.netio.getAllPowerSockets()
        except StandardError, error:
            print(str(error))
            return
        #self.netio.disconnect()
        for i in range(4):
            label_name = "socket"+str(i+1)+"_label"
            self.builder.get_object(label_name).set_text(self.builder.get_object(label_name).get_text()+' ("'+power_sockets[i].getName()+'")')
    
    
    
    def updateSystemSetup(self):
        try:
            deviceAlias = self.netio.getDeviceAlias()
            version = self.netio.getFirmwareVersion()
            systemTime = self.netio.getSystemTime().isoformat(" ")
            timezoneOffset = self.netio.getSystemTimezone()
            sntpSettings = self.netio.getSntpSettings()
        except StandardError, error:
            print(str(error))
            return
        #self.netio.disconnect()
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
        #self.netio.disconnect()
        self.updatePowerSocketStatus()

class ConnectionDetailDialog:
    def __init__(self,host='',username='admin',password='',port=1234, store_connection = True, store_password = False):
        self.builder = gtk.Builder()
        self.builder.add_from_file(getAbsoluteFilepath(CONNECTION_DETAIL_UI))
        self.dialog = self.builder.get_object("ConnectionDetailDialog")
        self.dialog.set_title("Provide connection details...")
        self.dialog.set_icon_from_file(getAbsoluteFilepath(PROGRAM_ICON))
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
        self.builder.get_object("store_connection").set_active(store_connection)
        self.builder.get_object("store_password").set_active(store_password)
        self.builder.get_object("action_area").set_focus_chain([self.builder.get_object("connect_button"), self.builder.get_object("abort_button")])
    
    def run(self):
        self.builder.connect_signals(self)
        self.builder.get_object("store_connection").connect("toggled", self.sensitivityUpdate)
        return self.dialog.run()
    
    def sensitivityUpdate(self, widget):
        self.builder.get_object("store_password").set_sensitive(self.builder.get_object("store_connection").get_active())
    
    def updateData(self):
        self.__host = self.builder.get_object("host_text").get_text()
        self.__username = self.builder.get_object("username_text").get_text()
        self.__pw = self.builder.get_object("password_text").get_text()
        try:
            self.__tcp_port = int(self.builder.get_object("port_text").get_text())
        except:
            self.__tcp_port = 0
            self.builder.get_object("port_text").set_text("0")
        self.__store_connection = self.builder.get_object("store_connection").get_active()
        self.__store_password = self.builder.get_object("store_password").get_active()
    
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
        data['store_connection'] = self.__store_connection
        data['store_password'] = self.__store_password
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

        self.window.set_size_request(470, 220)
        self.window.connect("delete_event", self.delete_event)

        # create a TreeStore with two string columns to use as the model
        self.treestore = gtk.TreeStore(str,str,str,str,str)

        devices = netio230a.get_all_detected_devices()
        if len(devices) > 0:
            self.auto_iter = self.treestore.append(None,['auto-detected devices','','','',''])
        else:
            self.treestore.append(None,['no auto-detected devices','','','',''])
        for device in devices:
            #   device name, IP, port, user, password
            self.treestore.append(self.auto_iter,[device[0],str(device[1][0])+'.'+str(device[1][1])+'.'+str(device[1][2])+'.'+str(device[1][3]),'','',''])
        
        # devices from configuration has the form [devicename, host, port, username, password]
        devices = configuration.getConfiguration()
        if len(devices) > 0:
            self.recently_iter = self.treestore.append(None,['previously used devices','','','',''])
        for device in devices:
            #   device name, IP, port, user, password
            self.treestore.append(self.recently_iter,[device[0],device[1],str(device[2]),device[3],device[4]])
        
        # more on TreeViews: <http://www.thesatya.com/blog/2007/10/pygtk_treeview.html>
        # and <http://www.pygtk.org/pygtk2tutorial/ch-TreeViewWidget.html#sec-TreeViewOverview>
        # create the TreeView using treestore
        self.treeview = gtk.TreeView(self.treestore)
        # create the TreeViewColumn to display the data
        self.tvc_device_name = gtk.TreeViewColumn('Device Name')
        self.tvc_ip = gtk.TreeViewColumn('IP Address')
        self.tvc_tcp_port = gtk.TreeViewColumn('TCP Port')
        self.tvc_user_name = gtk.TreeViewColumn('User Name')
        # set alignment of the column titles to right
        #self.tvc_ip.set_alignment(1.0)
        #self.tvc_tcp_port.set_alignment(1.0)
        # add tvcolumn to treeview
        self.treeview.append_column(self.tvc_device_name)
        self.treeview.append_column(self.tvc_ip)
        self.treeview.append_column(self.tvc_tcp_port)
        self.treeview.append_column(self.tvc_user_name)
        # create a CellRendererText to render the data
        self.cell = gtk.CellRendererText()
        self.cell_right_align = gtk.CellRendererText()
        self.cell_right_align.set_property('xalign', 1.0)
        # add the cell to the tvcolumn and allow it to expand
        self.tvc_device_name.pack_start(self.cell, True)
        self.tvc_ip.pack_start(self.cell_right_align, True)
        self.tvc_tcp_port.pack_start(self.cell_right_align, True)
        self.tvc_user_name.pack_start(self.cell, True)
        # set the cell "text" attribute to column 0 - retrieve text from that column in treestore
        self.tvc_device_name.add_attribute(self.cell, 'text', 0)
        self.tvc_ip.add_attribute(self.cell_right_align, 'text', 1)
        self.tvc_tcp_port.add_attribute(self.cell_right_align, 'text', 2)
        self.tvc_user_name.add_attribute(self.cell, 'text', 3)
        # make it searchable
        self.treeview.set_search_column(0)
        # Allow sorting on the column
        self.tvc_device_name.set_sort_column_id(0)
        self.tvc_ip.set_sort_column_id(1)
        self.tvc_tcp_port.set_sort_column_id(2)
        self.tvc_user_name.set_sort_column_id(3)
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
        stored_connection = False
        for arg in args:
            if type(arg)==gtk.TreeView:
                (model, treeiter) = arg.get_selection().get_selected()
                host = model.get_value(treeiter,1)
                parent_iter = model.iter_parent(treeiter)
                # compare the text (of the 1st col) of the parent node with the text of the recently_iter node
                try:
                    if model.get_value(self.recently_iter,0) == model.get_value(parent_iter,0):
                        stored_connection = True
                        tcp_port = model.get_value(treeiter,2)
                        username = model.get_value(treeiter,3)
                        password = model.get_value(treeiter,4)
                        store_password = False if password=='' else True
                except:
                    # we don't have recently used devices yet...
                    pass
                if host == '':
                    return
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
        if stored_connection:
            self.dl = ConnectionDetailDialog(host, username, password, tcp_port, stored_connection, store_password)
        else:
            self.dl = ConnectionDetailDialog(host)
        self.controller.deny_quit = True
        result = self.dl.run()
        self.controller.deny_quit = False
        while result == 1:
            data = self.dl.getData()
            try:
                netio = netio230a.netio230a(data['host'], data['username'], data['password'], True, data['tcp_port'])
                devicename = netio.getDeviceAlias()
                netio = None
                break
            except StandardError, error:
                print(str(error))
                netio = None
                continue_abort = gtk.MessageDialog(parent=self.dl.dialog, flags=gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK_CANCEL, message_format="Connection failed. \n\n"+str(error)+"\n\nChange connection details and try again?")
                response = continue_abort.run()
                continue_abort.destroy()
                if response == gtk.RESPONSE_OK:
                    self.controller.deny_quit = True
                    result = self.dl.run()
                    self.controller.deny_quit = False
                else:
                    result = 0
                    break
        
        self.dl.dialog.hide()
        del self.dl
        if result != 1:
            return
        
        # connection successful, do want to store the configuration?
        if data['store_connection'] == True:
            configuration.changeConfiguration(configuration.UPDATE, devicename, data['host'], data['tcp_port'], data['username'], data['password'] if data['store_password'] else '')
        else:
            configuration.changeConfiguration(configuration.REMOVE, devicename, data['host'], data['tcp_port'], data['username'], '')
            md = gtk.MessageDialog(self.window, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, "Connection details removed from configuration file.")
            md.run()
            md.destroy()
        self.controller.setNextStep("runDeviceController", host = data['host'], tcp_port = data['tcp_port'], username=data['username'], password = data['password'])
        #self.window.hide()
        self.window.destroy()
        gtk.main_quit()
        return False

class TrayIcon(gtk.StatusIcon):
    # reely adapted from the tracker-applet: <https://labs.codethink.co.uk/index.php/p/tracker/source/tree/master/python/applet/applet.py>
    # one more resource:
    # please note that the context menu (just as any other menu in Gnome will not have icons unless you set the gconf key /desktop/gnome/interface/menus_have_icons to true. For further information see <https://bugzilla.gnome.org/show_bug.cgi?id=557469>.
    def __init__(self,controller):
        gtk.StatusIcon.__init__(self)
        self.block_changes = True
        self.controller = controller
        self.set_disconnected_ui()
        self.set_from_file(getAbsoluteFilepath(PROGRAM_ICON))
        self.set_tooltip('NETIO-230A control')
        self.set_visible(True)
        self.connect('activate', self.on_activate)
        self.connect('popup-menu', self.on_popup_menu)
        self.block_changes = False
    
    def set_disconnected_ui(self):
        menu = '''
            <ui>
             <menubar name="Menubar">
              <menu action="Menu">
               <menuitem action="ConnectNote"/>
               <separator/>
               <menuitem action="About"/>
               <separator/>
               <menuitem action="Quit"/>
              </menu>
             </menubar>
            </ui>
        '''
        # order of the elements in the action tuples:
        # The name of the action. Must be specified.
        # The stock id for the action. Optional with a default value of None if a label is specified.
        # The label for the action. This field should typically be marked for translation, see the set_translation_domain() method. Optional with a default value of None if a stock id is specified.
        # The accelerator for the action, in the format understood by the gtk.accelerator_parse() function. Optional with a default value of None.
        # The tooltip for the action. This field should typically be marked for translation, see the set_translation_domain() method. Optional with a default value of None.
        # The callback function invoked when the action is activated. Optional with a default value of None.
        actions = [
            ('Menu',  None, 'Menu'),
            #('Search', None, '_Search...', None, 'Search files with MetaTracker', self.on_activate),
            ('ConnectNote', None, ' - please connect first... - ', None, 'Please connect to a NETIO-230A device to be able to power on/off sockets.', self.on_toggle),
            ('About', gtk.STOCK_ABOUT, '_About...', None, 'About NETIO-230A control', self.on_about),
            ('Quit', gtk.STOCK_QUIT, '_Quit', None, 'Quit the program', self.quit),]
        ag = gtk.ActionGroup('Actions')
        ag.add_actions(actions)
        self.manager = gtk.UIManager()
        self.manager.insert_action_group(ag, 0)
        self.manager.add_ui_from_string(menu)
        self.menu = self.manager.get_widget('/Menubar/Menu/About').props.parent
        connect_note = self.manager.get_widget('/Menubar/Menu/ConnectNote')
        image = gtk.Image()
        image.set_from_file(getAbsoluteFilepath(PROGRAM_ICON))
        connect_note.set_image(image)
        #search.get_children()[0].set_markup('<b>_Search...</b>')
        #search.get_children()[0].set_use_underline(True)
        #search.get_children()[0].set_use_markup(True)
        #search.get_children()[1].set_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU)

    def update_checkboxes(self,new_status):
        i = 1
        self.block_changes = True
        for socket in new_status:
            menu_item = self.manager.get_widget('/Menubar/Menu/Socket' + str(i))
            if menu_item == None:
                continue
            menu_item.set_label("_%d: %s" % (i, socket[0]))
            menu_item.set_active(socket[1])
            i += 1
        self.block_changes = False

    def set_connected_ui(self):
        menu = '''
            <ui>
             <menubar name="Menubar">
              <menu action="Menu">
               <menuitem action="Socket1"/>
               <menuitem action="Socket2"/>
               <menuitem action="Socket3"/>
               <menuitem action="Socket4"/>
               <separator/>
               <menuitem action="About"/>
               <separator/>
               <menuitem action="Quit"/>
              </menu>
             </menubar>
            </ui>
        '''
        actions = [
            ('Menu',  None, 'Menu'),
            #('Search', None, '_Search...', None, 'Search files with MetaTracker', self.on_activate),
            #('Preferences', gtk.STOCK_PREFERENCES, '_Preferences...', None, 'Change MetaTracker preferences', self.on_preferences),
            ('About', gtk.STOCK_ABOUT, '_About...', None, 'About NETIO-230A control', self.on_about),
            ('Quit', gtk.STOCK_QUIT, '_Quit', None, 'Quit the program', self.quit),]
        toggle_actions = [
            ('Socket1', None, '_1: Toggle Socket 1', None, 'Switch power socket 1 on or off.', self.on_toggle,True),
            ('Socket2', None, '_2: Toggle Socket 2', None, 'Switch power socket 2 on or off.', self.on_toggle),
            ('Socket3', None, '_3: Toggle Socket 3', None, 'Switch power socket 3 on or off.', self.on_toggle),
            ('Socket4', None, '_4: Toggle Socket 4', None, 'Switch power socket 4 on or off.', self.on_toggle),]
        ag = gtk.ActionGroup('Actions')
        ag.add_actions(actions)
        ag.add_toggle_actions(toggle_actions)
        self.manager = gtk.UIManager()
        self.manager.insert_action_group(ag, 0)
        self.manager.add_ui_from_string(menu)
        self.menu = self.manager.get_widget('/Menubar/Menu/About').props.parent
        #search = self.manager.get_widget('/Menubar/Menu/Search')
        #search.get_children()[0].set_markup('<b>_Search...</b>')
        #search.get_children()[0].set_use_underline(True)
        #search.get_children()[0].set_use_markup(True)
        #search.get_children()[1].set_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU)

    def quit(self, widget):
        if self.controller.deny_quit:
            self.controller.quit_requested()
        else:
            gtk.main_quit()

    def on_activate(self, data):
        #print("ok, here we want to toggle the visibility of the program...")
        self.controller.toggle_visibility()
    
    def on_toggle(self, action):
        if self.block_changes == True:
            return
        try:
            socket_name = action.get_name()
        except:
            raise NameError("actions seems to be no gtk.Action! something went wrong")
        if socket_name.find("Socket") != -1:
            try:
                #print("toggeling " + socket_name[6])
                self.controller.topical_window.netio.togglePowerSocketPower(int(socket_name[6]))
                #self.controller.topical_window.netio.disconnect()
                self.controller.topical_window.updatePowerSocketStatus()
            except:
                #print("sorry, log in first.")
                pass

    def on_popup_menu(self, status, button, time):
        self.menu.popup(None, None, None, button, time)

    #def on_preferences(self, data):
    #    print 'preferences'

    def on_about(self, data):
        about = AboutDialog()
        about.run()



class Controller(object):
    def run(self):
        self.nextStep = "runDeviceSelector"
        self.visible = True
        self.deny_quit = False
        self.icon = TrayIcon(self)
        while self.nextStep != "":
            if self.nextStep == "runDeviceSelector":
                self.nextStep = ""
                self.runDeviceSelector()
            elif self.nextStep == "runDeviceController":
                self.nextStep = ""
                self.runDeviceController(self.nextStepKWArgs)
    
    def quit_requested(self):
        try:
            self.topical_window.dl.dialog.present()
        except:
            pass
    
    def toggle_visibility(self):
        if self.visible == True:
            self.topical_window.window.hide()
            self.visible = False
        else:
            self.topical_window.window.show()
            self.visible = True
    
    def setNextStep(self,what, **kwargs):
        self.nextStep = what
        self.nextStepKWArgs = kwargs
    
    def runDeviceSelector(self):
        self.icon.set_disconnected_ui()
        self.topical_window = DeviceSelector(self)
        gtk.main()
        del self.topical_window
    
    def runDeviceController(self, connection_details):
        self.icon.set_connected_ui()
        self.topical_window = DeviceController(self, connection_details)
        gtk.main()
        self.topical_window.timer_continue = False
        del self.topical_window.netio

def debug(message, level):
    if DEBUG_MODE and level > DEBUG_LEVEL:
        print(message)

def main():
    controller = Controller()
    controller.run()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL) # ^C exits the application
    netio230a.TELNET_SOCKET_TIMEOUT = OVERWRITE_TELNET_SOCKET_TIMEOUT
    
    main()

