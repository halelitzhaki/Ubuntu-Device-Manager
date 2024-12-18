
# USB Gadget Setup Project

This project contains scripts and configuration files for setting up a USB gadget on a Raspberry Pi 4 using ConfigFS. The setup allows the Raspberry Pi to act as a USB device. The project includes setup scripts and a CSV file detailing USB vendor information.

## Files in the Project

1. **script.sh**  
   This script sets up a simple USB gadget via ConfigFS. It configures the gadget with attributes like manufacturer, serial number, product ID, and vendor ID. It also sets up various USB functions (like ECM and mass storage) and binds the gadget to a UDC driver.

2. **setup.sh**  
   This script prepares the Raspberry Pi 4 to support USB Gadget functionality. It:
   - Modifies `/boot/firmware/config.txt` to include necessary configurations for `dwc2`, `peripheral` mode, and `libcomposite`.
   - Updates `/boot/firmware/cmdline.txt` to load required modules (`dwc2`, `g_ether`).
   - Creates a systemd service (`usb_gadget_script.service`) to run the USB gadget setup script (`script.sh`) automatically at boot.
   - Reboots the system to apply the changes.

3. **vendors.csv**  
   A CSV file containing information about various USB devices, including Vendor IDs, Product IDs, Vendor Names, and Product Names. This file can be used for changing the USB gadget identifiers.

## Setup Instructions

### Requirements
- Raspberry Pi 4 with a USB hub connected to the USB-C power-in port.
- Kernel version >= 3.19 with `configfs` enabled.

### Step 1: Make 'scripts' directory in Documents
```bash
mkdir Documents/scripts/
```
Download the scripts into the scripts directory.

### Step 2: Run `setup.sh`
This script will configure your Raspberry Pi to support USB gadgets and create a systemd service to manage the gadget automatically.

```bash
sudo bash setup.sh
```

The system will reboot after the script completes. Make sure to save any work before running the script.

If everything is set up correctly, the service should be active and running.


## Troubleshooting
- If you encounter issues with the USB gadget not binding to the UDC driver, ensure there are no existing USB gadgets (e.g., using `g_*` modules). Remove any conflicting modules using `rmmod`.
- Review the system logs using `dmesg | grep dwc2` for errors related to `dwc2` or the USB gadget setup.
