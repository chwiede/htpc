#!/bin/bash

# READ WAKEUP-TIMESTAMP FROM VDR, SET TO RTC
# See also: http://www.mythtv.org/wiki/ACPI_Wakeup
# This Script has to be executed with root permissions.

# !!! IMPORTANT !!!
# You MUST disable hwclock updates. 
# see also: http://www.mythtv.org/wiki/ACPI_Wakeup#Disable_hwclock_updates
# otherwise your RTC-wakeup will be overwritten by your system.


# Configuration
DEVICE="/sys/class/rtc/rtc0/wakealarm"

# - - -

# get next wake timestamp from VDR. This is local time!
VDRWAKE=$(svdrpsend NEXT abs | grep -E -o '[0-9]{6,}')

if [[ -z "$VDRWAKE" ]]; then
	echo "VDR seems not to be running... no changes!"
	exit 1
fi

# ensure timestamp to be UTC
DATE=$(date -d @$VDRWAKE +%F" "%T)
TIMESTAMP=$(date -u --date "$DATE" +%s)

# clear RTC Wakeup, and set new date
echo 0 > $DEVICE
echo $TIMESTAMP > $DEVICE

# give out
cat /proc/driver/rtc | grep alrm

# hooray
exit 0
