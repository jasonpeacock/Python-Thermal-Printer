import logging

log = logging.getLogger(__name__)


class FakeHardware:
    """Fake printer hardware interface.

    Useful when GPIO is not available.
    """

    def __init__(self):
        log.debug("Initializing **fake** printer hardware interfaces")

    def led_on(self):
        pass

    def led_off(self):
        pass

    def button_state(self):
        # "Released" (un-pressed) button is True.
        return True


class Hardware:
    """Printer hardware interface.

    Manages the LED & button.
    """

    _BUTTON_PIN = 23
    _LED_PIN = 18

    def __init__(self):
        log.debug("Initializing printer hardware interfaces")
        import RPi.GPIO as GPIO

        self._GPIO = GPIO

        # Use Broadcom pin numbers (not Raspberry Pi pin numbers) for GPIO.
        self._GPIO.setmode(self._GPIO.BCM)

        # Enable LED and button (w/pull-up on latter).
        self._GPIO.setup(self._LED_PIN, self._GPIO.OUT)
        self._GPIO.setup(self._BUTTON_PIN, self._GPIO.IN, pull_up_down=self._GPIO.PUD_UP)

    def led_on(self):
        log.debug("Turning LED on")
        self._GPIO.output(self._LED_PIN, self._GPIO.HIGH)

    def led_off(self):
        log.debug("Turning LED off")
        self._GPIO.output(self._LED_PIN, self._GPIO.LOW)

    def button_state(self):
        return self._GPIO.input(self._BUTTON_PIN)
