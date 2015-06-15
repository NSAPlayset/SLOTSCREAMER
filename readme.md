Basics:
======
The way it works is that the USB3380 chip has usb endpoints - PCIIN and PCIOUT - that give the usb host the ability to generate any kind of PCIe packet. It doesn't give full control of all header fields, but you can issue mem, io, and cfg reads and writes. Inception only scratches the surface, but is an easy and cool demonstration. Right now it's pretty slow, but i believe that's due to pyusb/libusb and a few other inefficiencies. theoretically it should be able to dump 4gb of memory in a matter of seconds, not 40 minutes.

Video Demo:
===========
https://www.youtube.com/watch?v=SvnvOXXAxaI

Getting Hardware:
=================
The PLX USB3380 is available for about $15. A custom DIY PCB is in progress but not ready yet.
USB3380 reference boards work fine but need firmware to be flashed. They can be aquired from PLX as part of a costly kit, or bought directly form the distributor, Bplus technologies. All of the below are the same company:

http://www.bplus.com.tw/PLX.html

http://www.hwtools.net/PLX.html

http://www.aliexpress.com/store/group/PLX-Series/706012_250803066.html

Confirmed working:
==================
* USB3380, both in PCIe adapter and ExpressCard adapters 
* PP3380 - but this card ships with a large EEPROM that requires 2-byte addressing, see below
* OWC Mercury Helios TB enclosure
* Sonnet Echo Pro TB enclosure

Does not work:
==============
* EC3380-AB small expresscard, EEPROM does not appear to work properly, so it can't work at all without PCIe-side drivers. This is a bummer cause it would've been a very compact combo with the sonnet echo pro.

Making a SLOTSCREAMER out of a PLX USB3380:
=========================================
All the months of toiling trying to prototype with linux usb gadget drivers were overcomplicated and went nowhere.
If you build an eeprom image all you have to do is set a usb enabled bit after pcie powers up. All the other default settings are actually completely sufficient to make it all work. SLOTSCREAMER.bin is attached. PLX provides windows and linux tools to program the firmware, or you could use a hardware programmer. To use the plx tools:

* download sdk, linux package only, from: http://www.plxtech.com/products/sdk/ You need to register to get access.
* unzip, then untar
* export PLX_SDK_DIR=..pathtofiles/PlxSdk
* cd PlxSdk/PlxApi
* make
* cd ../Driver
* ./builddriver Svc
* cd ../
* ./Bin/Plx_load Svc
* cd Samples/PlxCm
* make
* ./App/PlxCm

PlxCm is their command line interface. it should automatically choose your usb3380. type:
show current eeprom state:  "eep"
load slotscreamer config: "eep_load SLOTSCREAMER.bin"
confirm loading: "eep"

That's it, your usb3380 reference board is now a SLOTSCREAMER


Notes for the PP3380:
====================
The PP3380 may have a larger eeprom that requires two-byte addressing, which PlxCm doesn't do by default. In that case use PlxEe and specify the address width and file to load. You also have to bridge jumper 3 to connect the eeprom.
* cd Samples/PlxEe
* make
* ./App/PlxEe -w 2 -l slotscreamer.bin

Running inception:
===============
Slotscreamer support is now incorporated upstream into inception, so this fork is no longer current.
https://github.com/carmaa/inception

Files:
======
* ./inception_pci contains a version of inception designed for SLOTSCREAMER
* ./slotscreamer-test.py is a simple set of test functions ot make sure it works

TODO:
=====
We have not thoroughly tested inception for passoword bypass. In the near future, we intend to go through the list of known working OSs that inception can bypass and confirm it works of debug why it doesn't

Changelog:
=========
The changes are essentially:
* added a SLOTSCREMER class to inception/util.py modeled after MemoryFile
* added necessary imports to util.py
* added pciemode to cfg.py and -N NativePCIe option in incept
* added switches for pcimode to both screenlock.py and memdump.py
* implemented caching for reads
* implemented cache invalidation after writes
* implemented proper responses to non-dword-aligned accesses


