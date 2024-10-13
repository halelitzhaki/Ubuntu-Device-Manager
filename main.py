from core.device_manager import monitor_usb_devices
from ml_model.model import train_model
import getpass
from gui.get_sudo_password_popup import get_sudo_password_gui  # Import the GUI function

if __name__ == "__main__":
    # Prompt for the sudo password using the GUI
    sudo_password = get_sudo_password_gui()

    # If no password is provided, exit the program
    if not sudo_password:
        print("No password provided. Exiting...")
        exit(1)

    # Train the model when the program starts
    train_model()

    # Start monitoring USB devices with the sudo password
    monitor_usb_devices(sudo_password)
