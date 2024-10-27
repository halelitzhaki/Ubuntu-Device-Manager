import subprocess
from loguru import logger
from utils.root_process_launcher import RootProcessLauncher
from core.device_utils import update_udev_rules


def disable_auto_mount(root_process_launcher: RootProcessLauncher) -> None:
    """ Disable auto-mounting """
    disable_command = 'ACTION=="add", SUBSYSTEM=="block", ENV{UDISKS_IGNORE}="1"'
    echo_command = 'tee -a /etc/udev/rules.d/99-disable-usb-automount.rules'
    try:
        # Pass the sudo password and run the echo command to append to the file
        root_process_launcher.execute_with_input(echo_command, disable_command)

        # Reload udev rules and trigger them to apply changes
        update_udev_rules(root_process_launcher)
        logger.info(f"Auto-mount disabled successfully")

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to disable automount")


def enable_auto_mount(root_process_launcher: RootProcessLauncher) -> None:
    """ Enable auto-mounting """
    echo_command = 'tee -a /etc/udev/rules.d/99-disable-usb-automount.rules'
    try:
        # Pass the sudo password and run the echo command to append to the file
        root_process_launcher.execute(echo_command)

        # Reload udev rules and trigger them to apply changes
        update_udev_rules(root_process_launcher)
        logger.info(f"Auto-mount enable successfully")

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to enable automount")

