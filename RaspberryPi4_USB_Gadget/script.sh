#!/bin/bash

# This script will setup a simple USB gadget via ConfigFS.
# In order to use it, you must have kernel >= 3.19 and configfs enabled
# when the kernel was compiled (it usually is).

# variables and strings
MANUFACTURER="Kingston Technology"                                            #  manufacturer attribute
SERIAL="1234567890"                                               #  device serial number
IDPRODUCT="0x1666"                                                #  hex product ID, issued by USB Group
IDVENDOR="0x0951"                                                 #  hex vendor ID, assigned by USB Group
PRODUCT=" DataTraveler"                                           #  cleartext product description
MAX_POWER_MA=120                                                  #  max power this configuration can consume in mA

# Gadget configuration
rmmod g_ether
modprobe libcomposite                                             #  load configfs
modprobe dwc2

# Create the USB gadget directory
mkdir /sys/kernel/config/usb_gadget/test_gadget
cd /sys/kernel/config/usb_gadget/test_gadget

# Set vendor and product IDs
echo $IDPRODUCT > idProduct
echo $IDVENDOR > idVendor

# Set up strings (English language, 0x409)
mkdir strings/0x409
echo $SERIAL > strings/0x409/serialnumber
echo $MANUFACTURER > strings/0x409/manufacturer
echo $PRODUCT > strings/0x409/product  # This line sets the overall gadget's product name

# Set up configuration
mkdir configs/c.1
echo $MAX_POWER_MA > configs/c.1/MaxPower

# Add mass storage function
mkdir functions/mass_storage.usb0
dd if=/dev/zero of=/home/user/usb_image.img bs=1M count=64
mkfs.vfat /home/user/usb_image.img
echo /home/user/usb_image.img > functions/mass_storage.usb0/lun.0/file
ln -s functions/mass_storage.usb0 configs/c.1/

# Bind the gadget
ls /sys/class/udc/ > UDC                                          #  bind gadget to UDC driver (brings gadget online). This will only
                                                                  #  succeed if there are no gadgets already bound to the driver. Do
                                                                  #  lsmod and if there's anything in there like g_*, you'll need to
                                                                  #  rmmod it before bringing this gadget online. Otherwise you'll get
                                                                  #  "device or resource busy."
dmesg | grep dwc2                                                 # make sure gadget loaded successfully
