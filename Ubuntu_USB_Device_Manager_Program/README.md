
# USB Device Manager

## Overview

The **USB Device Manager** is a Python application that monitors, manages, and controls USB devices connected to a system. It provides functionalities for detecting, allowing, or blocking USB devices based on user input and machine learning predictions. The application integrates with Linux's `udev` subsystem to manage USB devices and offers a GTK-based graphical user interface (GUI) for user interactions.

## Features

- **USB Device Monitoring**: Continuously monitors USB device connections and disconnections.
- **User Prompt for USB Devices**: Displays a popup when a new USB device is connected, allowing the user to choose whether to allow or block the device.
- **Automatic Device Handling**: Uses a machine learning model to predict whether to automatically allow or block USB devices based on previous user decisions.
- **GUI for Sudo Password**: Prompts the user for the sudo password using a GUI dialog to gain the necessary permissions for managing USB devices.
- **Automatic Mount/Unmount**: Supports automatically mounting and unmounting USB devices based on user input.
- **udev Integration**: Manages `udev` rules to control device permissions and behaviors.
- **Auto-Mount Control**: Enables or disables the auto-mount feature of USB devices.

## Requirements

- Python 3.6+
- Dependencies:
  - `pyudev`
  - `loguru`
  - `scikit-learn`
  - `joblib`
  - `PyGObject`
  - `python3-tk`
  - `pexpect`
- `sudo` permissions are required to run the application due to the nature of USB device management.

## Installation

1. Install the required Python libraries:
   ```bash
   pip install pyudev loguru scikit-learn joblib PyGObject
   ```

2. Ensure the application has the necessary permissions by running it with `sudo` or by providing your password through the GUI prompt.

## Usage

Run the application with the following command:

```bash
python3 main.py
```

### Program Flow

1. **Sudo Password Prompt**: The application first asks for the sudo password using a GTK-based GUI. If no password is provided, the application exits.
2. **Model Training**: The application loads logged USB device data and trains a machine learning model to automatically allow or block devices based on past behavior.
3. **USB Device Monitoring**: The `USBDeviceManager` class manages monitoring and responding to USB events.
4. **User Interaction**: When a new USB device is connected, the user is prompted via a GUI to allow or block the device. The user's decision is logged for future model training.

## Code Structure

- `main.py`: Entry point of the application. Sets up the environment and starts USB monitoring.
- `core/`:
  - `usb_device.py`: Defines the `USBDevice` dataclass.
  - `device_manager.py`: Contains the `USBDeviceManager` class responsible for monitoring and managing USB devices.
  - `device_utils.py`: Contains utility functions for interacting with devices (e.g., mounting, unmounting, logging).
- `gui/`:
  - `get_sudo_password.py`: Provides a GTK dialog for collecting the sudo password.
  - `usb_alert.py`: Displays a dialog when a USB device is detected, allowing the user to permit or block it.
- `ml_model/`:
  - `model.py`: Manages model training and prediction.
- `utils/`:
  - `auto_mount_handler.py`: Controls auto-mount behavior using `udev` rules.
  - `root_process_launcher.py`: Handles executing commands with root privileges using the provided sudo password.

## Logging

Logs are stored in `data/usb_device_logs.json` and include details of each USB connection event along with the user’s decision. This information is used for model training and making future predictions.

## Example Workflow

1. The application starts and prompts the user for the sudo password.
2. The machine learning model is trained on historical USB connection data.
3. The application monitors for new USB connections. When detected:
   - If the model confidently predicts "allow" based on past user behavior, the device is automatically mounted.
   - If the device is not recognized or the model is uncertain, the user is prompted to allow or block the device.
4. The user's decision is logged for future reference and model improvement.

## Security Considerations

- **Sudo Permissions**: The application requires elevated privileges to manage USB devices. The password is securely handled using Python's subprocess to ensure minimal exposure, you don't need to run the program using sudo.
- **udev Rules**: The application modifies `udev` rules to control auto-mount behavior. Ensure you review these rules before deploying on sensitive systems.
