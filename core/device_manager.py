import os
import subprocess
import pyudev
import time
import json

from core.usb_device import USBDevice
from core.device_utils import get_block_device, get_lsblk_device, log_usb_device
from gui.usb_alert import show_usb_alert
from ml_model.model import predict

LOG_FILE = 'data/usb_device_logs.json'


class USBDeviceManager:
    """ Manages the monitoring and blocking/allowing of USB devices. """

    DEBOUNCE_TIME = 1

    def __init__(self, sudo_password):
        self.sudo_password = sudo_password
        self.seen_devices = set()

    def allow_usb_device(self, device):
        """ Logic to allow and automatically mount the USB device. """
        print(f"Allowing and mounting USB Device: {device.vendor_id} - {device.product_id}")

        # Get the block device (e.g., /dev/sdb1)
        block_device = get_lsblk_device(device.device_node)

        if not block_device:
            print(f"Unable to identify block device for {device.device_node}.")
            return

        # Define a mount point (you can customize this path)
        whoami = subprocess.run(['whoami'], capture_output=True, text=True)
        mount_point = f'/media/{whoami.stdout.strip()}/{device.serial}' # For example, mounting by the device's serial

        # Create the mount point directory if it doesn't exist
        if not os.path.exists(mount_point):
            mkdir_command = ['mkdir', mount_point]
            subprocess.run(mkdir_command)

        # Mount the block device to the mount point
        mount_command = ['sudo', '-S', 'mount', block_device, mount_point]

        try:
            # Execute the mount command
            subprocess.Popen(mount_command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)\
                .communicate(input=f'{self.sudo_password}'.encode())
            print(f"USB Device: {device.vendor_id} - {device.product_id} mounted successfully at {mount_point}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to mount the USB device: {e}")

    def block_usb_device(self, device):
        """ Block the USB device by unmounting and powering it off. """
        print(f"Blocking USB Device: {device.vendor_id} - {device.product_id}")

        block_device = get_block_device(device.device_node)

        if not block_device:
            print(f"Unable to identify block device for {device.device_node}.")
            return

        # The udev rule to block the USB device
        blocking_command = f'ATTR{{idVendor}}=="{device.vendor_id}", ATTR{{idProduct}}=="{device.product_id}", ATTR{{authorized}}="0"'

        # Command to append the blocking rule to the udev file
        echo_command = ['sudo', '-S', 'tee', '-a', '/etc/udev/rules.d/99-usb-blacklist.rules']

        try:
            # Pass the sudo password and run the echo command to append to the file
            subprocess.Popen(echo_command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL) \
                .communicate(input=f'{self.sudo_password}\n{blocking_command}\n'.encode())

            # Reload udev rules and trigger them to apply changes
            update_commands = [
                ['sudo', '-S', 'udevadm', 'control', '--reload'],
                ['sudo', '-S', 'udevadm', 'trigger']
            ]
            for command in update_commands:
                subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL) \
                    .communicate(input=f'{self.sudo_password}\n'.encode())

            print(f"USB Device: {device.vendor_id} - {device.product_id} blocked successfully")

        except subprocess.CalledProcessError as e:
            print(f"Failed to block the USB device: {e}")

    def monitor_usb_devices(self):
        """ Monitor USB devices and handle them based on user input and model predictions. """
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='usb')

        print("Monitoring USB devices. Press Ctrl+C to stop.")

        try:
            for device in iter(monitor.poll, None):
                if device.action == 'add':
                    # Fetch device information
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
                        print(f"Device {device_node} already processed, skipping...")
                        continue

                    # Add to seen_devices to prevent processing duplicates
                    self.seen_devices.add(device_node)

                    # Prepare device info
                    usb_device = USBDevice(vendor_id, product_id, serial, device_node)

                    # Check if the model predicts an automatic allow/block
                    prediction = predict(vars(usb_device))
                    # prediction = "false"

                    if prediction == 'allow':
                        print(f"Automatically allowing device: {usb_device.vendor_id}")
                        self.allow_usb_device(usb_device)
                    else:
                        # If the prediction is unknown, ask the user
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

                        else:
                            self.block_usb_device(usb_device)

        except KeyboardInterrupt:
            print("\nStopping USB device monitoring.")

