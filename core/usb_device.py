from dataclasses import dataclass


@dataclass
class USBDevice:
    """ Represents a USB Device with relevant properties. """
    vendor_id: str
    product_id: str
    serial: str
    device_node: str

    def __post_init__(self):
        if not self.serial:
            self.serial = "Unknown"

    def __repr__(self) -> str:
        return str(self.__dict__)