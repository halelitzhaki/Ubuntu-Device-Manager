import subprocess
import pyudev
import time
import json
from loguru import logger

from Ubuntu_USB_Device_Manager_Program.core.usb_device import USBDevice
from Ubuntu_USB_Device_Manager_Program.core.device_utils import get_block_device, get_lsblk_device, log_usb_device, update_udev_rules, mount_device, unmount_device
from Ubuntu_USB_Device_Manager_Program.gui.usb_alert import show_usb_alert
from Ubuntu_USB_Device_Manager_Program.ml_model.model import predict
from Ubuntu_USB_Device_Manager_Program.utils.auto_mount_handler import enable_auto_mount, disable_auto_mount
from Ubuntu_USB_Device_Manager_Program.utils.root_process_launcher import RootProcessLauncher

LOG_FILE = 'data/usb_device_logs.json'


class USBDeviceManager:
    """ Manages the monitoring and blocking/allowing of USB devices. """

    DEBOUNCE_TIME = 1

    def __init__(self, sudo_password: str) -> None:
        self.seen_devices = set()
        self.root_process_launcher = RootProcessLauncher(sudo_password)

    def allow_usb_device(self, device: USBDevice) -> None:
        """ Logic to allow and automatically mount the USB device. """
        logger.info(f"Allowing and mounting USB Device: {device.vendor_id} - {device.product_id}")

        # Get the block device (e.g., /dev/sdb1)
        block_device = get_lsblk_device(device.device_node)

        if not block_device:
            logger.error(f"Unable to identify block device for {device.device_node}.")
            return

        mount_device(self.root_process_launcher, device, block_device)

    def block_usb_device(self, device: USBDevice) -> None:
        """ Block the USB device by unmounting and powering it off. """
        logger.info(f"Blocking USB Device: {device.vendor_id} - {device.product_id}")

        block_device = get_block_device(device.device_node)

        if not block_device:
            logger.error(f"Unable to identify block device for {device.device_node}.")
            return

        # The udev rule to block the USB device
        blocking_command = f'ATTR{{idVendor}}=="{device.vendor_id}", ATTR{{idProduct}}=="' \
                           f'{device.product_id}", ATTR{{authorized}}="0"'

        # Command to append the blocking rule to the udev file
        echo_command = 'tee -a /etc/udev/rules.d/99-usb-blacklist.rules'

        try:
            # Running the blocking command with root privileges
            self.root_process_launcher.execute_with_input(echo_command, blocking_command)
            update_udev_rules(self.root_process_launcher)
            logger.info(f"USB Device: {device.vendor_id} - {device.product_id} blocked successfully")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to block the USB device: {e}")

    def monitor_usb_devices(self) -> None:
        """ Monitor USB devices and handle them based on user input and model predictions. """
        # Create interface for interacting with udev subsystem
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='usb')  # Filtering only the USB events

        disable_auto_mount(self.root_process_launcher)

        logger.info("Monitoring USB devices. Press Ctrl+C to stop.")

        try:
            for device in iter(monitor.poll, None):
                if device.action == 'add':  # New USB device was plugged
                    # Fetch USB device information
                    vendor_id = device.get('ID_VENDOR_ID')
                    product_id = device.get('ID_MODEL_ID')
                    serial = device.get('ID_SERIAL_SHORT')
                    device_node = device.device_node

                    # If incomplete info, debounce and wait for complete event
                    if not vendor_id or not product_id:
                        time.sleep(self.DEBOUNCE_TIME)
                        continue

                    # Check if we've already processed this device (avoid duplicate popups)
                    if device_node in self.seen_devices:
                        logger.error(f"Device {device_node} already processed, skipping...")
                        continue

                    # Add to seen_devices to prevent processing duplicates
                    self.seen_devices.add(device_node)

                    # Parse device info
                    usb_device = USBDevice(vendor_id, product_id, serial, device_node)

                    # Check if the model predicts an automatic allow/block
                    prediction = predict(vars(usb_device))

                    if prediction == 'allow':
                        logger.info(f"Automatically allowing device: {usb_device.vendor_id}")
                        self.allow_usb_device(usb_device)
                    else:
                        # If the prediction is unknown, ask the user with popup
                        user_choice, auto_allow = show_usb_alert(vars(usb_device))

                        # Log and take action based on user choice
                        log_usb_device(vars(usb_device), user_choice)

                        if user_choice == 'allow':
                            self.allow_usb_device(usb_device)

                            # Update vendor allow count only if auto-allow checkbox is checked
                            if auto_allow:
                                with open('data/vendor_allow_counts.json', 'r+') as f:
                                    try:
                                        vendor_allow_count = json.load(f)
                                    except (FileNotFoundError, json.JSONDecodeError):
                                        vendor_allow_count = {}

                                    if vendor_id not in vendor_allow_count:
                                        vendor_allow_count[vendor_id] = 0
                                    vendor_allow_count[vendor_id] += 1

                                    f.seek(0)
                                    json.dump(vendor_allow_count, f)

                        elif user_choice == 'block':
                            self.block_usb_device(usb_device)

                        else:
                            continue
                elif device.action == 'remove': # USB device was unplugged
                    # Handle device removal
                    if device.device_node in self.seen_devices:
                        self.seen_devices.remove(device.device_node)
                        logger.info(f"USB Device {device.device_node} removed.")

                        # Deleting the mount point of the device
                        unmount_device(self.root_process_launcher, device)

        except KeyboardInterrupt:
            # Return system to its original state
            enable_auto_mount(self.root_process_launcher)
            logger.info("Stopping USB device monitoring.")
