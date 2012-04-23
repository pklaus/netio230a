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
try:
    import netio230a
except:
    from . import netio230a


host = "192.168.1.2"
pw = "your choosen password"
tcp_port = 23


from bottle import Bottle, run, request, static_file, HTTPError


api = Bottle()

def getnetio():
    try:
        netio = netio230a.netio230a(host, "admin", pw, True, tcp_port)
    except:
        raise HTTPError(code=500, output='Could not communicate with the device')
    return netio

@api.post('/port')
def port():
    port_num = int(request.forms.get('port'))
    power_on = request.forms.get('power_on').lower() in ['true', '1', 'on']
    netio = getnetio()
    netio.setPowerSocketPower(port_num,power_on)
    status = dict()
    status['port'] = port_num
    status['power_on'] = power_on
    status['success'] = True
    netio = None
    return status


@api.route('/status')
def status():
    netio = getnetio()
    status = dict()
    status['version'] = netio.getFirmwareVersion()
    power_sockets = []
    for power_socket_object in netio.getAllPowerSockets():
        power_sockets.append( {'power_on': power_socket_object.getPowerOn(), 'name': power_socket_object.getName()} )
    status['power_sockets'] = power_sockets
    status['device_alias'] = netio.getDeviceAlias()
    status['system_discoverable'] = netio.getSystemDiscoverableUsingTool()
    netio = None
    return status


root = Bottle()
root.mount(api, '/api')

@root.route('/static/<path:path>')
def static(path):
    return static_file(path, root='./resources')

@root.route('/')
def index():
    return static('webserver-ajax-template.html')
    
## Run with cherrypy server via IPv4:
run( root, server='cherrypy', host="0.0.0.0", port=8080)
## Run with cherrypy server via IPv6:
#run( root, server='cherrypy', host="::", port=8080)

## Run with bottle's standard server (IPv4):
#run( root, host="localhost", port=8080, debug=True)
