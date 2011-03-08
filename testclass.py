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


# This is the unittest for the netio230a class. Written in PyUnit:
#  <http://docs.python.org/library/unittest.html>

import unittest
import netio230a

# To simulate the NETIO230A device:
import threading
import fakeserver

#DEBUG = True
DEBUG = False

if DEBUG:
    # use the Python profiler to know what's slow (<http://docs.python.org/library/profile.html>):
    import cProfile

class TestNETIO230A(unittest.TestCase):

    def setUp(self):
        """
        setUp() gets executed before every test_SOMETHING() test in this class
        """
        self.fake_server = fakeserver.FakeNetio230a(("", 0), fakeserver.FakeNetio230aHandler)
        self.fake_server_ip, self.fake_server_port = self.fake_server.server_address
        # Start a thread with the server -- that thread will then start one more thread for each request
        # (but we want to listen for shutdown requests every millisecond)
        self.server_thread = threading.Thread(target=self.fake_server.serve_forever,args=(0.001,))
        # Exit the server thread when the main thread terminates
        self.server_thread.daemon = True
        self.server_thread.start()

    def tearDown(self):
        """
        tearDown() gets executed after every test_SOMETHING() test in this class
        """
        self.fake_server.shutdown()
        # we need server_close() too because the socket would remain opened otherwise:
        self.fake_server.server_close() # see <http://stackoverflow.com/questions/5218159>

    def test_for_invalid_server(self):
        ## Test for exception:
        self.assertRaises(NameError,netio230a.netio230a,"x 400.1.1.1", "admin", "password", True, 1234)
        #netio230a.netio230a("300.1.1.1", "admin", "password", True, 1234)

    def test_connect_to_fake_server(self):
        netio = netio230a.netio230a("localhost","admin", "password", True, self.fake_server_port)

    #def test_valid_requests(self):
    #    pass
        #version = netio.getFirmwareVersion()
        #swDelay = netio.getSwitchDelay()
        #power_sockets = netio.getAllPowerSockets()
        #power_socket_1_status = netio.getPowerSocketSetup(0)
        #deviceAlias = netio.getDeviceAlias()
        #watchdogSettings1 = netio.getWatchdogSettings(1)
        #networkSettings = netio.getNetworkSettings()
        #dnsServer = netio.getDnsServer()
        #systemDiscoverable = netio.getSystemDiscoverableUsingTool()
        #sntpSettings = netio.getSntpSettings()
        #systemTime = netio.getSystemTime()
        #timezoneOffset = netio.getSystemTimezone()

if __name__ == '__main__':
    try:
        cProfile.run('unittest.main()')
    except:
        unittest.main()
