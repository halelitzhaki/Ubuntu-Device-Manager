class USBDevice:
    """ Represents a USB Device with relevant properties. """
    def __init__(self, vendor_id, product_id, serial, device_node):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.serial = serial if serial else "Unknown"
        self.device_node = device_node

    def __repr__(self):
        return f"USBDevice(vendor_id={self.vendor_id}, product_id={self.product_id}, serial={self.serial}, device_node={self.device_node})"
