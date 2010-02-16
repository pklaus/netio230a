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



"""
This module is made to simplify the process of saving and retrieving saved credentials from previous connections for the other modules of the project.
"""

import json
from datetime import datetime
import os

CONFIGURATION_FILE = os.path.expanduser("~/.netio230a/connections.json")

REMOVE = -1
UPDATE = 2

def changeConfiguration(action, devicename, host, port, username, password):
    try:
        os.makedirs(os.path.split(CONFIGURATION_FILE)[0])
    except StandardError, error:
        pass
        
    try:
        # try to get stored configuration (if it exists)
        configuration = getConfiguration()
    except StandardError, error:
        # or create an empty list for the new configuration
        configuration = []
    try:
        old_device, new_device = None, None
        for device in configuration:
            if device[0] == devicename and device[1] == host and device[2] == port and device[3] == username:
                old_device = device
                new_device = [devicename, host, port, username, password, datetime.now().isoformat()]
        
        if action == UPDATE:
            if new_device == None and old_device == None:
                configuration.append([devicename, host, port, username, password, datetime.now().isoformat()])
            else:
                configuration.remove(old_device)
                configuration.append(new_device)
        elif action == REMOVE:
            if old_device != None:
                configuration.remove(old_device)
            
        outfile = open(CONFIGURATION_FILE,'w')
        json.dump(configuration,outfile)
        outfile.close()
        return True
    except StandardError, error:
        print str(error)
        return False

def getConfiguration():
    try:
        infile = open(CONFIGURATION_FILE,'r')
        configuration = json.load(infile)
        infile.close()
        return configuration
    except StandardError, error:
        return []

if __name__ == "__main__":
    print("You have %d connections stored in your configuration file." % len(getConfiguration()) )



