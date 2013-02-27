#!/bin/bash

# enforce usb hid driver
modprobe -r usbhid
modprobe usbhid

# start X
su htpc -c 'xinit /usr/share/htpcutils/xinitrc' &
export DISPLAY=:0.0

# start power manager
/usr/bin/htpcutils/powermanager/controller.py

# ready
exit 0
