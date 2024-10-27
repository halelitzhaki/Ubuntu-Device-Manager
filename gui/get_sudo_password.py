import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class SudoPasswordDialog(Gtk.Dialog):
    def __init__(self) -> None:
        super().__init__(title="Sudo Password", flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT)

        # Set dialog properties
        self.set_default_size(300, 100)

        # Create the label and password entry field
        label = Gtk.Label(label="Please enter your sudo password:")
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)  # Mask password input

        # Connect the "activate" signal to trigger the "OK" response when Enter is pressed
        self.password_entry.connect("activate", self.on_password_entry_activate)

        # Add the label and entry to a vertical box
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)
        vbox.pack_start(label, expand=False, fill=False, padding=0)
        vbox.pack_start(self.password_entry, expand=False, fill=False, padding=0)

        # Add "OK" and "Cancel" buttons
        self.add_button("OK", Gtk.ResponseType.OK)
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)

        # Add the vertical box to the dialog's content area
        box = self.get_content_area()
        box.add(vbox)

        # Show all widgets
        self.show_all()

    def on_password_entry_activate(self, widget) -> None:
        """ Trigger the "OK" response when Enter is pressed. """
        self.response(Gtk.ResponseType.OK)

    def get_password(self) -> str:
        """ Retrieve the entered password from the entry field. """
        return self.password_entry.get_text()


def get_sudo_password_gui() -> str:
    """ Display a GTK dialog to get the sudo password. """
    dialog = SudoPasswordDialog()

    # Run the dialog and block until a response is received
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        password = dialog.get_password()
    else:
        password = None

    # Explicitly destroy the dialog
    dialog.destroy()

    # Process pending GTK events (ensures the dialog is fully closed)
    while Gtk.events_pending():
        Gtk.main_iteration()

    return password if password else None
