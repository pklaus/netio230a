TODO
====

Class
-----

* switch on port for a configurable amount of time (to make coffee).
  (this can be done by setting the timer! SNTP should be however disabled for security reasons!)
* implement the watchdog functionality (representation in port class)
* implement the timer functionality (representation in port class)
* maybe cleanup of the mixed use of mixedCase and lower_case_with_underscores
  (the later is preferred).
* type safety (?!)

GUI
---

* more threading (when changing from one tab to another, we want to do see
  status updates - YES. But first change to that tab and then do the update.)
* save information in a configuration file:
  * remember program status (activated tab etc.)
* preferences dialog:
  * automatic status updates (en-/disable, change frequency)
  * en-/disable logging
* ability to change the names of the ports via the user interface
* switch on a power socket for a configurable amount of time

less important are:

* ability to change the watchdog settings for each port
* ability to change the time of the device, the DNS and IP settings, the system name.

Allready Implemented
--------------------

* save information in a configuration file:
  * remember multiple connection details and login credentials
* login using connect button in the GUI
* display socket name in GUI switchbox according to the name given in the webinterface
* implemented all documented commands found in the manual up to command "port" on page 19.
* automatic status updates (every 3 seconds)
* logging capabilities for the class added (the GUI makes use of it)
* link to open the devices website with a single click on the GUI
* concurrent access to the netio230a library secured (by waiting for the other request or throwing an exception)

