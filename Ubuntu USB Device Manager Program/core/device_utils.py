import subprocess
import os
import json
import pyudev
from loguru import logger
from utils.root_process_launcher import RootProcessLauncher
from core.usb_device import USBDevice

LOG_FILE = 'data/usb_device_logs.json'


def get_block_device(device_node: str) -> '':
    """ Get the block device (e.g., /dev/sdb1) associated with the USB device using udevadm. """
    try:
        # Use udevadm info to get the block device associated with the USB bus path
        command = ['udevadm', 'info', '--query=all', '--name', device_node]
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        # Parse the output to find the DEVNAME (the actual block device like /dev/sdb1)
        for line in result.stdout.splitlines():
            if 'DEVNAME=' in line:
                return line.split('=')[1]  # Extract the block device path

    except subprocess.CalledProcessError as e:
        logger.error(f'Error identifying block device for {device_node}: {e}')
        return None


def get_lsblk_device(device: str) -> '':
    """ Get the block device path (e.g., /dev/sda1) for the USB device. """
    # Create interface for accessing udev subsystem
    context = pyudev.Context()

    # Find the parent of the device in the USB subsystem
    device_parent = None
    for dev in context.list_devices(subsystem='usb'):
        if dev.device_node == device:
            device_parent = dev
            break

    if not device_parent:
        logger.error(f"Device parent not found for {device}")
        return None

    # Look for a block device (partition) whose parent is the USB device
    for block_device in context.list_devices(subsystem='block', DEVTYPE='partition'):
        if device_parent in block_device.ancestors:
            return block_device.device_node

    return None


def log_usb_device(device_info: {}, decision: str) -> None:
    """ Log device information with a decision (allow or block). """
    # Creating log file
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as file:
            json.dump([], file)

    with open(LOG_FILE, 'r+') as file:
        try:
            logs = json.load(file)
        except json.JSONDecodeError:
            logs = []

        device_info['decision'] = decision  # Add the decision field
        logs.append(device_info)

        file.seek(0)
        json.dump(logs, file, indent=4)  # Inserting the device info to log file


def update_udev_rules(root_process_launcher: RootProcessLauncher) -> None:
    """ Reload udev rules and trigger them to apply changes """
    # Making udev update commands
    update_commands = ['udevadm control --reload', 'udevadm trigger']
    # Running commands with root privileges
    for command in update_commands:
        root_process_launcher.execute(command)


def mount_device(root_process_launcher: RootProcessLauncher, device: USBDevice, block_device: '') -> None:
    """ Creating directory in /[user]/media and mounting the usb device to it """
    # Get the current user
    whoami = subprocess.run(['whoami'], capture_output=True, text=True).stdout.strip()

    # Define a temporary mount point under /media
    mount_point = f'/media/{whoami}/{device.serial}'

    # Create the mount point directory if it doesn't exist
    if not os.path.exists(mount_point):
        mkdir_command = f'mkdir {mount_point}'
        root_process_launcher.execute(mkdir_command)

    # Mount the block device to the mount point
    mount_command = f'mount {block_device} {mount_point}'

    try:
        # Execute the mount command
        root_process_launcher.execute(mount_command)
        logger.info(f"USB Device: {device.vendor_id} - {device.product_id} mounted successfully at {mount_point}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to mount the USB device: {e}")


def unmount_device(root_process_launcher: RootProcessLauncher, device: USBDevice) -> None:
    """ Unmounting device from /[user]/media/ and deleting the directory """
    # Get the current user
    whoami = subprocess.run(['whoami'], capture_output=True, text=True).stdout.strip()

    with open(LOG_FILE, 'r') as file:
        log_entries = json.load(file)

    device_details = {}
    for entry in log_entries:
        if entry['device_node'] == device.device_node:
            device_details['serial'] = entry['serial']
            device_details['vendor_id'] = entry['vendor_id']
            device_details['product_id'] = entry['product_id']

            break
    if not device_details:
        logger.error(f"Failed to find the USB device: {device.device_node} mount point")

    # Define the mount point
    mount_point = f"/media/{whoami}/{device_details['serial']}"

    # Unmount the block device
    unmount_command = f'umount {mount_point}'

    try:
        # Execute the unmount command
        root_process_launcher.execute(unmount_command)
        logger.info(f"USB Device: {device_details['vendor_id']} - {device_details['product_id']} "
                    f"unmounted successfully from {mount_point}")

        # Remove the mount point directory if it exists
        if os.path.exists(mount_point):
            rm_command = f"rm -rf {mount_point}"
            root_process_launcher.execute(rm_command)
            logger.info(f"Mount point {mount_point} removed.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to unmount the USB device: {e}")
