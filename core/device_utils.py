import json
import os
import subprocess

LOG_FILE = 'data/usb_device_logs.json'


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


def allow_usb_device(device_info):
    """ Logic to allow USB device (could be left as no-op if no blocking mechanism needed). """
    print(f"Allowing USB Device: {device_info['vendor_id']} - {device_info['product_id']}")


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


def block_usb_device(device_info, sudo_password):
    """ Block the USB device by unmounting and powering it off. """
    print(f"Blocking USB Device: {device_info['vendor_id']} - {device_info['product_id']}")

    device_node = device_info['device']
    block_device = get_block_device(device_node)

    if not block_device:
        print(f"Unable to identify block device for {device_node}.")
        return

    vendor_id = device_info['vendor_id']
    product_id = device_info['product_id']

    # The udev rule to block the USB device
    blocking_command = f'ATTR{{idVendor}}=="{vendor_id}", ATTR{{idProduct}}=="{product_id}", ATTR{{authorized}}="0"'

    # Command to append the blocking rule to the udev file
    echo_command = ['sudo', '-S', 'tee', '-a', '/etc/udev/rules.d/99-usb-blacklist.rules']

    try:
        # Pass the sudo password and run the echo command to append to the file
        subprocess.Popen(echo_command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)\
            .communicate(input=f'{sudo_password}\n{blocking_command}\n'.encode())

        # Reload udev rules and trigger them to apply changes
        update_commands = [
            ['sudo', '-S', 'udevadm', 'control', '--reload'],
            ['sudo', '-S', 'udevadm', 'trigger']
        ]
        for command in update_commands:
            subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)\
                .communicate(input=f'{sudo_password}\n'.encode())

        print(f"USB Device: {vendor_id} - {product_id} blocked successfully")

    except subprocess.CalledProcessError as e:
        print(f"Failed to block the USB device: {e}")
