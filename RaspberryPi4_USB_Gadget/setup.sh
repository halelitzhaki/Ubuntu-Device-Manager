#!/bin/bash

# This script will setup a Raspberry Pi 4 to support USB Gadget.
# Since only the USB-C (i.e. power-in port) has UDC in it,
# you must to connect a powerful USB hub to the rpi and then connect it to your pc.

sed -i '/\[cm5\]/,/\[all\]/ { /\[all\]/!d; }' /boot/firmware/config.txt
sudo echo -e "dtoverlay=dwc2\ndr_mode=peripheral\ndtoverlay=libcomposite\n" >> /boot/firmware/config.txt                               #  Open boot hardware settings and configuration file
sudo echo " modules-load=dwc2,g_ether " >> /boot/firmware/cmdline.txt

sudo echo -e "[Unit]\nDescription=USB Gadget Setup Service\nAfter=network.target\n\n[Service]\nType=simple\nExecStart=/bin/bash /home/user/Documents/scripts/script.sh\nUser=root\nGroup=root\nRemainAfterExit=yes\n\n[Install]\nWantedBy=multi-user.target" > /etc/systemd/system/usb_gadget_script.service

sudo systemctl daemon-reload
sudo systemctl enable usb_gadget_script.service
sudo systemctl start usb_gadget_script.service

sudo reboot  # Reboot to apply changes
