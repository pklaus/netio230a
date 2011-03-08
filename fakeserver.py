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


# This is a fake Koukaam NETIO230A telnet server.
# It tries to imitate the behaviour of the original device.
# The reason this exitsts is mainly the unittest for the netio230a class.

import SocketServer
import threading
import random

# For sys.exit():
import sys

# for the client:
import asyncore, socket

#import pdb ## use with pdb.set_trace()

########## ----------- code for the fake server (imitating the Koukaam NETIO230A) -------------

# Koukaam Netio230A Behaviour:
N_WELCOME = "100 HELLO %X - KSHELL V1.2"
N_OK = "250 OK"
N_AUTH_ERR = "503 INVALID LOGIN"
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
        auth = False
        while not auth:
            data = self.receive()
            if "login" in data.strip().lower():
                auth = True
            if auth:
                self.send(N_OK)
                break
            else:
                self.send(N_AUTH_ERR)
        # now we serve all incoming requests:
        while True:
            data = self.receive()
            if self.means(data,'port list'):
                self.send(''.join([str(int(status)) for status in fake_server.getOutlets()]))
            if self.means(data,'quit'):
                break
        self.send(N_BYE)
    
    def means(self,data,what):
        return data.strip().lower() == what


class FakeNetio230a(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def __init__(self, server_address, RequestHandlerClass):
        ### Seems like we don't really need this line (at least with Python 2.7 on Mac OS X):
        self.allow_reuse_address = True
        ## with Python 3 we would use something like:
        #super( FakeNetio230a, self ).__init__(server_address, RequestHandlerClass)
        ## instead we have to call the constructor of TCPServer explicitly using Python 2.X
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)

        self.outlets = [False,False,False,False]

    def setOutlet(self, which, to):
        self.outlets[which]=bool(to)

    def getOutlets(self):
        return self.outlets

fake_server = FakeNetio230a(("", 0), FakeNetio230aHandler)

def start_server(show_client):
    fake_server_ip, fake_server_port = fake_server.server_address
    print("Fake Netio230A server reachable on 'localhost' on port %i" % fake_server_port)
    if show_client:
        # If we want a client to show up, we have to put the server to a background thread:
        server_thread = threading.Thread(target=fake_server.serve_forever,args=(0.3,))
        server_thread.daemon = True
        server_thread.start()
        try:
            client = NetcatClient(fake_server_ip, fake_server_port)
            client_thread = threading.Thread(target=client.run)
            client_thread.daemon = True
            client_thread.start()
            while client.connected:
                client.buffer = raw_input()
        except NameError:
            print "The client shut down the connection. Closing."
        except KeyboardInterrupt:
            print("  [CTRL]-[C] catched, exiting.")
    else:
        try:
            fake_server.serve_forever(0.3)
        except KeyboardInterrupt:
            print("  [CTRL]-[C] catched, exiting.")
            sys.exit(1)
    sys.exit(0)

class NetcatClient2(asyncore.dispatcher):
    def interactive(self,host,port):
        self.client.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect( (host, port) )
        read_thread = threading.Thread(target=self.read)
        read_thread.daemon = True
        read_thread.start()
        while True:
            self.client.send(raw_input())
    def read(self):
        while True:
            print self.client.recv(8192)

class NetcatClient(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (host, port) )
        self.connected = True
        self.buffer = ""
    def run(self):
        asyncore.loop(1)
    def handle_connect(self):
        print "connection started"
    def handle_close(self):
        self.close()
        self.connected = False
    def handle_read(self):
        print self.recv(8192)
    def writable(self):
        return (len(self.buffer) > 0)
    def handle_write(self):
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]


if __name__ == '__main__':
    start_server(True)
