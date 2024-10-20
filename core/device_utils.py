import subprocess
import os
import json
import pyudev

LOG_FILE = 'data/usb_device_logs.json'


def get_block_device(device_node):
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
        print(f"Error identifying block device for {device_node}: {e}")
        return None


def get_lsblk_device(device):
    """ Get the block device path (e.g., /dev/sda1) for the USB device. """
    context = pyudev.Context()

    # Find the parent of the device in the USB subsystem
    device_parent = None
    for dev in context.list_devices(subsystem='usb'):
        if dev.device_node == device:
            device_parent = dev
            break

    if not device_parent:
        print(f"Device parent not found for {device}")
        return None

    # Look for a block device (partition) whose parent is the USB device
    for block_device in context.list_devices(subsystem='block', DEVTYPE='partition'):
        if device_parent in block_device.ancestors:
            return block_device.device_node

    return None


def log_usb_device(device_info, decision):
    """ Log device information with a decision (allow or block). """
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
        json.dump(logs, file, indent=4)


def disable_auto_mount(sudo_password):
    """ Disable auto-mounting """
    disable_command = 'ACTION=="add", SUBSYSTEM=="block", ENV{UDISKS_IGNORE}="1"'
    echo_command = ['sudo', '-S', 'tee', '-a', '/etc/udev/rules.d/99-disable-usb-automount.rules']
    try:
        # Pass the sudo password and run the echo command to append to the file
        subprocess.Popen(echo_command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL) \
            .communicate(input=f'{sudo_password}\n{disable_command}\n'.encode())

        # Reload udev rules and trigger them to apply changes
        update_commands = [
            ['sudo', '-S', 'udevadm', 'control', '--reload'],
            ['sudo', '-S', 'udevadm', 'trigger']
        ]
        for command in update_commands:
            subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL) \
                .communicate(input=f'{sudo_password}\n'.encode())

        print(f"Auto-mount disabled successfully")

    except subprocess.CalledProcessError as e:
        print(f"Failed to disable automount")
