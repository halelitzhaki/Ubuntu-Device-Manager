import subprocess
from loguru import logger
from Ubuntu_USB_Device_Manager_Program.utils.root_process_launcher import RootProcessLauncher
from Ubuntu_USB_Device_Manager_Program.core.device_utils import update_udev_rules


def disable_auto_mount(root_process_launcher: RootProcessLauncher) -> None:
    """ Disable auto-mounting """
    disable_command = 'ACTION=="add", SUBSYSTEM=="block", ENV{UDISKS_IGNORE}="1"'
    tee_command = 'tee -a /etc/udev/rules.d/99-disable-usb-automount.rules'
    try:
        # Pass the sudo password and run the echo command to append to the file
        root_process_launcher.execute_with_input(tee_command, disable_command)

        # Reload udev rules and trigger them to apply changes
        update_udev_rules(root_process_launcher)
        logger.info(f"Auto-mount disabled successfully")

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to disable automount")


def enable_auto_mount(root_process_launcher: RootProcessLauncher) -> None:
    """ Enable auto-mounting """
    truncate_command = 'truncate -s 0 /etc/udev/rules.d/99-disable-usb-automount.rules'
    try:
        # Pass the sudo password and run the echo command to append to the file
        root_process_launcher.execute(truncate_command)

        # Reload udev rules and trigger them to apply changes
        update_udev_rules(root_process_launcher)
        logger.info(f"Auto-mount enable successfully")

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to enable automount")

