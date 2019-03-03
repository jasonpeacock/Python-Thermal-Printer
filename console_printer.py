import logging

log = logging.getLogger(__name__)


class ConsolePrinter:
    """Default console printer, prints to STDOUT.

    Useful as a replacement when `Adafruit_Thermal` or other printers are not available.
    """

    def __init__(self):
        log.debug("Initializing **console** printer")

    def print(self, content):
        print(content)

    def println(self, content):
        print(content)

    def feed(self, rows):
        for _ in range(rows):
            print()

    def inverseOn(self):
        pass

    def inverseOff(self):
        pass

    def underlineOn(self):
        pass

    def underlineOff(self):
        pass

    def boldOn(self):
        pass

    def boldOff(self):
        pass

    def printImage(self, image, LaaT=False):
        pass
