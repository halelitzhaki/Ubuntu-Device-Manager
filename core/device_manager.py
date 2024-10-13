import pyudev
import time
from core.device_utils import log_usb_device, block_usb_device, allow_usb_device
from gui.usb_alert_popup import show_usb_alert

# Keep track of already processed devices
seen_devices = set()

# Delay to allow device info to complete (in seconds)
DEBOUNCE_TIME = 1

def monitor_usb_devices(sudo_password):
    # Initialize the context and monitor for device changes
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
                    # Skipping incomplete device info
                    time.sleep(DEBOUNCE_TIME)  # Wait a bit to allow device initialization
                    continue

                # Check if we've already processed this device (avoid duplicate popups)
                if device_node in seen_devices:
                    print(f"Device {device_node} already processed, skipping...")
                    continue

                # Add to seen_devices to prevent processing duplicates
                seen_devices.add(device_node)

                # Prepare device info for logging and decisions
                device_info = {
                    'vendor_id': vendor_id,
                    'product_id': product_id,
                    'serial': serial if serial else "Unknown",
                    'device': device_node
                }

                # Trigger GUI alert to allow/block the device and get the user's decision
                user_choice = show_usb_alert(device_info)

                # Log only if valid and processed by the user
                log_usb_device(device_info, user_choice)

                # Allow or block the device based on user choice
                if user_choice == 'allow':
                    allow_usb_device(device_info)
                else:
                    block_usb_device(device_info, sudo_password)

    except KeyboardInterrupt:
        print("\nStopping USB device monitoring.")
        return


if __name__ == "__main__":
    monitor_usb_devices()
