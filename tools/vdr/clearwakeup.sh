#!/bin/bash

# CLEAR WAKEUP, SET TO RTC
# See also: http://www.mythtv.org/wiki/ACPI_Wakeup
# This Script has to be executed with root permissions.

# Configuration
# - - -

# The RTC-device
DEVICE="/sys/class/rtc/rtc0/wakealarm"

# - - -

# clear RTC Wakeup
echo 0 > $DEVICE

# give out
cat /proc/driver/rtc | grep alrm

# hooray
exit 0
