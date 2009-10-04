#!/bin/sh

## Multiple power schedule script
## Script 2 of 2
## piping power-fr.sh output to telnet

## you have to set the correct paths from / to the script and telnet

/conf/scripts/power/power-fr.sh | /usr/bin/telnet

