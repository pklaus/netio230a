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

# more helpers:
import time

FAKEDEVICE_ADDRESS = "localhost"
FAKEDEVICE_TCPPORT = 38838

class TestNETIO230A(unittest.TestCase):

    def setUp(self):
        self.fake_server = FakeNetio230a(("", FAKEDEVICE_TCPPORT), FakeNetio230aHandler)
        # Start a thread with the server -- that thread will then start one more thread for each request
        self.server_thread = threading.Thread(target=self.fake_server.serve_forever)
        # Exit the server thread when the main thread terminates
        self.server_thread.setDaemon(True)
        self.server_thread.start()

    def tearDown(self):
        self.fake_server.shutdown()
        self.server_thread.join()
        print "join ended."

    def test_for_invalid_server(self):
        ## Test for exception:
        self.assertRaises(NameError,netio230a.netio230a,"1.1.12", "admin", "password", True, 1234)

    # def test_valid_requests(self):
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


    def test_connect_to_fake_server(self):
        netio = netio230a.netio230a(FAKEDEVICE_ADDRESS,"admin", "password", True, FAKEDEVICE_TCPPORT)


# Koukaam Netio230A Behaviour:
N_WELCOME = "100 HELLO %s - KSHELL V1.2"
N_OK = "250 something"
N_BYE = "110 BYE"
N_LINE_ENDING = "\r\n"

class FakeNetio230aHandler(SocketServer.BaseRequestHandler):

    def send(self,message):
        self.request.send(message+N_LINE_ENDING)

    def receive(self):
        return self.request.recv(1024)

    def handle(self):
        self.send(N_WELCOME % "9D555C8E")
        data = self.receive()
        #cur_thread = threading.currentThread()
        #response = "%s: %s" % (cur_thread.getName(), data)
        #self.request.send(response)
        self.send(N_OK)
        print self.receive()
        self.request.send('hi ' + str(self.client_address) + '\n')
        data = 'dummy'
        while data:
            data = self.request.recv(1024)
            self.request.send(data)
            if data.strip() == 'bye':
                return

    #def finish(self):
    #    self.request.send('bye ' + str(self.client_address) + '\n')



class FakeNetio230a(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


if __name__ == '__main__':
    unittest.main()
