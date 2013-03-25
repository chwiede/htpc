# HTPC Tools

This is a toolset for your **Arch-Linux** based home theater-computer using

* XBMC
* tvheadend

## htpcutils

contains a python controller started by systemd. Its used for powermanagement and wake-up support via rtc device.

Htpcutils will detect whe the HTPC woke up:

* Recordmode is entered, if woke up for a record
* Watchmode is entered, if woke up normally

In recordmode openbox is started and not XBMC - this saves some power.
If you press the powerbutton, the mode is changed from record to watch and vice versa.


## tbs6981

contains an automatic updater for tbs6981 DVB-S2 PCIe card. It looks for the newest drivers, download it and compiles.

**WARNING**: due to the used v4l-sources existing kernel-v4l-modules will be deleted. 
That means, your arch-modules will be older after install and some DVB-Devices won't work!
