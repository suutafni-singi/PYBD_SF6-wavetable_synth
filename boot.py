# boot.py -- run on boot-up
# can run arbitrary Python, but best to keep it minimal

import machine
import pyb
pyb.country('US') # ISO 3166-1 Alpha-2 code, eg US, GB, DE, AU
pyb.main('main.py') # main script to run after this one
machine.freq(216000000)
#pyb.usb_mode('VCP+MSC')
pyb.usb_mode('VCP+MSC',msc=(pyb.Flash(),))
if pyb.SDCard().present():
    os.mount(pyb.SDCard(), '/sd')
    sys.path[1:1] = ['/sd', '/sd/lib']
# act as a serial and a storage device
#pyb.usb_mode('VCP+HID') # act as a serial device and a mouse
