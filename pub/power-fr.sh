#!/bin/sh

## Multiple power schedule script
## Script 1 of 2
## Script to be executed on Friday after poweron from daily schedule, setting shutdown to Monday 03:00
## Poweron setting to Sunday is ignored because power is already switched on
## After executing Monday Shutdown, Netio will do automaticaly daily schedule ( 03:00 OFF, 16:00 ON)
## until script runs again to activate the weekend poweron setting

#replace ip with yours
host=192.168.x.y
port=1234

# you have to replace your admin username and password
login="login user pwd"

p1_timermode="port setup 1 port1 timer 5 1"
p2_timermode="port setup 2 port2 timer 5 1"
p3_timermode="port setup 3 port3 timer 5 1"
p4_timermode="port setup 4 port4 timer 5 1"

p1_poweron2=`date -v+2d +%Y/%m/%d,`
p2_poweron2=`date -v+2d +%Y/%m/%d,`
p3_poweron2=`date -v+2d +%Y/%m/%d,`
p4_poweron2=`date -v+2d +%Y/%m/%d,`

p1_poweroff2=`date -v+3d +%Y/%m/%d,`
p2_poweroff2=`date -v+3d +%Y/%m/%d,`
p3_poweroff2=`date -v+3d +%Y/%m/%d,`
p4_poweroff2=`date -v+3d +%Y/%m/%d,`

p1_switch2="port timer 1 dt daily "${p1_poweron2}"15:54:30 "${p1_poweroff2}"03:03:00 1111111"
p2_switch2="port timer 2 dt daily "${p2_poweron2}"15:54:00 "${p2_poweroff2}"03:02:30 1111111"
p3_switch2="port timer 3 dt daily "${p3_poweron2}"15:53:30 "${p3_poweroff2}"03:02:00 1111111"
p4_switch2="port timer 4 dt daily "${p4_poweron2}"15:52:00 "${p4_poweroff2}"03:01:00 1111111"

echo open $host $port
sleep 2
echo $login
sleep 2
#just for testing
echo $portl
sleep 2
#ensuring ports are on timermode
echo $p1_timermode
sleep 3
echo $p2_timermode
sleep 3
echo $p3_timermode
sleep 3
echo $p4_timermode
sleep 5
#setting schedule
echo $p1_switch2
sleep 2
echo $p2_switch2
sleep 2
echo $p3_switch2
sleep 2
echo $p4_switch2
sleep 2
echo exit

