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


### HowTo
#  To run this Bottle web application, you have to install
#  the python modules
#    * bottle
#    * cherrypy
#  You can do this via `pip install bottle`  etc.

#  Then you should adjust the `host`, `pw` and `tcp_port`
#  settings in this file.
#  When finished, run this file via `./webserver.py`
#  and you should be able to reach the site via
#  http://localhost:8080


## import the netio230a class:
import netio230a




from bottle import Bottle, run, request, static_file, HTTPError, PluginError


import inspect

class Netio230aPlugin(object):
    ''' This plugin passes a netio230a class handle to route callbacks
    that accept a `netio` keyword argument.
    It is based on the example on
    http://bottlepy.org/docs/stable/plugindev.html#plugin-example-sqliteplugin
    '''
    name = 'netio'
    api = 2

    def __init__(self, host, username='admin', password='admin', tcp_port=23, logfile=None, keyword='netio'):
         self.host = host
         self.username = username
         self.password = password
         self.tcp_port = tcp_port
         self.logfile = logfile
         self.keyword = keyword

    def setup(self, app):
        ''' Make sure that other installed plugins don't affect the same
            keyword argument.'''
        for other in app.plugins:
            if not isinstance(other, Netio230aPlugin): continue
            if other.keyword == self.keyword:
                raise PluginError("Found another Netio230a plugin with "\
                "conflicting settings (non-unique keyword).")
        try:
            self.netio = netio230a.netio230a(self.host, self.username, self.password, True, self.tcp_port)
        except Exception as e:
            raise PluginError("Could not connect to the NETIO230A with hostname %s (username: %s). Error: %s" % (self.host, self.username, e) )
        if self.logfile:
            try:
                self.netio.enable_logging(open(self.logfile,'w'))
            except:
                raise PluginError("Could not enable logging to this log file: " + str(self.logfile))

    def apply(self, callback, context):
        keyword = self.keyword
        # Test if the original callback accepts a 'netio' keyword.
        # Ignore it if it does not need a handle.
        args = inspect.getargspec(context.callback)[0]
        if keyword not in args:
            return callback

        def wrapper(*args, **kwargs):
            netio = self.netio
            # Add the connection handle as a keyword argument.
            kwargs[keyword] = netio

            try:
                rv = callback(*args, **kwargs)
            except NameError as e:
                raise HTTPError(503, "NETIO230A not available: " + str(e) )
            finally:
                #netio.disconnect()
                pass
            return rv

        # Replace the route callback with the wrapped one.
        return wrapper

    def close(self):
        self.netio.disconnect()
        self.netio = None

api = Bottle()

@api.post('/port')
def port(netio):
    port_num = int(request.forms.get('port'))
    power_on = request.forms.get('power_on').lower() in ['true', '1', 'on']
    netio.setPowerSocketPower(port_num,power_on)
    status = dict()
    status['port'] = port_num
    status['power_on'] = power_on
    status['success'] = True
    return status

@api.route('/ports/status')
def ports_status(netio):
    status = dict()
    power_sockets = []
    for power_on in netio.getPowerSocketList():
        power_sockets.append( {'power_on': power_on} )
    status['power_sockets'] = power_sockets
    return status

@api.route('/system/status')
def system_status(netio):
    status = dict()
    status['version'] = netio.getFirmwareVersion()
    status['device_alias'] = netio.getDeviceAlias()
    status['system_discoverable'] = netio.getSystemDiscoverableUsingTool()
    power_sockets = []
    for power_socket_object in netio.getAllPowerSockets():
        power_sockets.append( {'power_on': power_socket_object.getPowerOn(), 'name': power_socket_object.getName()} )
    status['power_sockets'] = power_sockets
    return status

root = Bottle()
root.mount('/api', api)

@root.route('/static/<path:path>')
def static(path):
    return static_file(path, root='./resources')

@root.route('/')
def index():
    return static('webserver-ajax-template.html')


def main():
    import argparse
    parser = argparse.ArgumentParser(
      description='Start a server to store location information.' )
    parser.add_argument('netio230a_host', metavar="NETIO230A_HOST",
      help='The IP of your NETIO-230A.')
    parser.add_argument('--port', '-p', type=int, default=8080,
      help='The port to run the web server on.')
    parser.add_argument('--ipv6', '-6', action='store_true',
      help='Listen to incoming connections via IPv6 instead of IPv4.')
    parser.add_argument('--debug', '-d', action='store_true',
      help='Start in debug mode (with verbose HTTP error pages.')
    parser.add_argument('--netio230a-port', type=int, default=1234,
      help='The username of your NETIO-230A.')
    parser.add_argument('--netio230a-username', default="admin",
      help='The username of your NETIO-230A.')
    parser.add_argument('--netio230a-password', default="admin",
      help='The password of your NETIO-230A.')
    parser.add_argument('--logfile', '-l', default="./webserver-log.txt",
      help='The file to store the server log in.')
    args = parser.parse_args()
    if args.debug and args.ipv6:
        args.error('You cannot use IPv6 in debug mode, sorry.')

    netio_plugin = Netio230aPlugin(args.netio230a_host, args.netio230a_username, args.netio230a_password, args.netio230a_port, logfile=args.logfile)
    api.install(netio_plugin)

    if args.debug:
        run(root, host='0.0.0.0', port=args.port, debug=True, reloader=True)
    else:
        if args.ipv6:
            run(root, host='::', server='cherrypy', port=args.port)
        else:
            run(root, host='0.0.0.0', server='cherrypy', port=args.port)

if __name__ == "__main__":
    main()
