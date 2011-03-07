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
import socket
import threading
import SocketServer
import random

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
        self.fake_server = FakeNetio230a(("", 0), FakeNetio230aHandler)
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

    #def test_for_invalid_server(self):
    #    ## Test for exception:
    #    self.assertRaises(NameError,netio230a.netio230a,"x 400.1.1.1", "admin", "password", True, 1234)
    #    #netio230a.netio230a("300.1.1.1", "admin", "password", True, 1234)

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


########## ----------- code for the fake server (imitating the Koukaam NETIO230A) -------------

# Koukaam Netio230A Behaviour:
N_WELCOME = "100 HELLO %X - KSHELL V1.2"
N_OK = "250 something"
N_NAC = "503 problem"
N_BYE = "110 BYE"
N_LINE_ENDING = "\r\n"

class FakeNetio230aHandler(SocketServer.BaseRequestHandler):

    def send(self,message):
        self.request.send(message+N_LINE_ENDING)

    def receive(self):
        return self.request.recv(1024)

    def handle(self):
        # First, we have to send the welcome message (including the salt for the md5 password hash):
        self.send(N_WELCOME % random.randint(0, 2**32-1) )
        # now we wait for incoming authentication requests:
        data = self.receive()
        auth = False
        while not auth:
            if "login" in data.strip().lower():
                auth = True
            if auth:
                self.send(N_OK)
            else:
                self.send(N_NAC)
        # now we serve all incoming requests:
        while True:
            data = self.request.recv(1024)
            if data.strip().lower() == 'quit':
                break
            self.send(data)
        self.send(N_BYE)


class FakeNetio230a(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, server_address, RequestHandlerClass):
        ### Seems like we don't really need this line (at least with Python 2.7 on Mac OS X):
        self.allow_reuse_address = True
        ## with Python 3 we would use something like:
        #super( FakeNetio230a, self ).__init__(server_address, RequestHandlerClass)
        ## instead we have to call the constructor of TCPServer explicitly using Python 2.X
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)


if __name__ == '__main__':
    try:
        cProfile.run('unittest.main()')
    except:
        unittest.main()
