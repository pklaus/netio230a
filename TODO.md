TODO
====

Class
-----

* switch on port for a configurable amount of time (to make coffee).
  (this can be done by setting the timer! SNTP should be however disabled for security reasons!)
* implement the watchdog functionality (representation in port class)
* implement the timer functionality (representation in port class)
* maybe cleanup of the mixed use of mixedCase and lower_case_with_underscores
  (the latter is preferred).
* type safety (?!)

GUI
---

* show an error message when almost all requests fail
  (depending on the reason why they fail...). This may be:
  "The NETIO-230A seems to be unavailable at the moment. Disconnecting."
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

Other
-----

* Investigate whether the fakeserver could be implemented using [twisted](http://twistedmatrix.com).

