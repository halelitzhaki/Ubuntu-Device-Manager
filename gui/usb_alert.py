import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class USBAlertDialog(Gtk.Dialog):
    def __init__(self, device_info: {}) -> None:
        super().__init__(title="USB Device Alert", flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT)

        # Set dialog properties
        self.set_default_size(300, 200)

        # Create a vertical box to hold the label and checkbox
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)  # Add padding around the box

        # Create the label with the device information
        label = Gtk.Label(label=f"USB Device Detected:\n\n"
                                f"Vendor ID: {device_info['vendor_id']}\n"
                                f"Product ID: {device_info['product_id']}\n"
                                f"Serial: {device_info['serial']}\n\n"
                                f"Do you want to allow or block this device?")

        # Add the label to the vertical box
        vbox.pack_start(label, expand=False, fill=False, padding=0)

        # Add a checkbox for auto-allow with extra padding between the label and the checkbox
        self.auto_allow_checkbox = Gtk.CheckButton(label="Automatically allow this type of device in the future")
        vbox.pack_start(self.auto_allow_checkbox, expand=False, fill=False, padding=20)  # Add padding for space

        # Add "Allow" and "Block" buttons to the dialog
        self.add_button("Allow", Gtk.ResponseType.YES)
        self.add_button("Block", Gtk.ResponseType.NO)

        # Add the vbox containing the label and checkbox to the dialog's content area
        box = self.get_content_area()
        box.add(vbox)

        # Show all widgets in the dialog
        self.show_all()

    def is_auto_allow(self) -> bool:
        """ Return whether the checkbox is active. """
        return self.auto_allow_checkbox.get_active()


def show_usb_alert(device_info: {}) -> []:
    """ Shows a GTK dialog asking the user whether to allow or block the USB device, with an auto-allow option. """
    dialog = USBAlertDialog(device_info)

    # Run the dialog and block until a response is received
    response = dialog.run()

    # Handle the response and close the dialog
    if response == Gtk.ResponseType.YES:
        decision = 'allow'
    elif response == Gtk.ResponseType.NO:
        decision = 'block'
    else:
        decision = 'block'  # Default to blocking if no valid response

    auto_allow = dialog.is_auto_allow()  # Check if auto-allow is selected

    # Explicitly destroy the dialog
    dialog.destroy()

    # Process pending GTK events (ensures the dialog is fully closed)
    while Gtk.events_pending():
        Gtk.main_iteration()

    return decision, auto_allow
