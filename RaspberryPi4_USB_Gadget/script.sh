#!/bin/bash

# This script will setup a simple USB gadget via ConfigFS.
# In order to use it, you must have kernel >= 3.19 and configfs enabled
# when the kernel was compiled (it usually is).

# variables and strings
MANUFACTURER="SanDisk"                                            #  manufacturer attribute
SERIAL="1234567890"                                               #  device serial number
IDPRODUCT="0x5567"                                                #  hex product ID, issued by USB Group
IDVENDOR="0x0781"                                                 #  hex vendor ID, assigned by USB Group
PRODUCT=" Cruzer Blade"                                           #  cleartext product description
CONFIG_NAME="Configuration 1"                                     #  name of this configuration
MAX_POWER_MA=120                                                  #  max power this configuration can consume in mA
PROTOCOL=1                                                        #  1 for keyboard. see usb spec
SUBCLASS=1                                                        #  it seems either 1 or 0 works, dunno why
REPORT_LENGTH=8                                                   #  number of bytes per report
DESCRIPTOR=/config/usb_gadget/keyboardgadget/kybd-descriptor.bin  #  binary blob of report descriptor, see HID class spec


# gadget configuration
rmmod g_ether
modprobe libcomposite                                             #  load configfs
modprobe dwc2
mkdir /sys/kernel/config/usb_gadget/test_gadget                   #  make a new gadget skeleton
cd /sys/kernel/config/usb_gadget/test_gadget                      #  cd to gadget dir
echo $IDPRODUCT > idProduct
echo $IDVENDOR > idVendor
mkdir strings/0x409
echo $SERIAL > strings/0x409/serialnumber
echo $MANUFACTURER > strings/0x409/manufacturer
echo $PRODUCT > strings/0x409/product
mkdir configs/c.1                                                 #  make the skeleton for a config for this gadget
echo $MAX_POWER_MA > configs/c.1/MaxPower
mkdir functions/ecm.usb0                                          #  add hid function (will fail if kernel < 3.19, which hid was added in)
ln -s functions/ecm.usb0 configs/c.1/
mkdir functions/mass_storage.usb0
dd if=/dev/zero of=/home/user/usb_image.img bs=1M count=64
mkfs.vfat /home/user/usb_image.img
echo /home/user/usb_image.img > functions/mass_storage.usb0/lun.0/file
ln -s functions/mass_storage.usb0 configs/c.1/

# binding
ls /sys/class/udc/ > UDC                                          #  bind gadget to UDC driver (brings gadget online). This will only
                                                                  #  succeed if there are no gadgets already bound to the driver. Do
                                                                  #  lsmod and if there's anything in there like g_*, you'll need to
                                                                  #  rmmod it before bringing this gadget online. Otherwise you'll get
                                                                  #  "device or resource busy."
dmesg | grep dwc2                                                 # make sure gadget loaded successfully