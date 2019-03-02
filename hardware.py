import logging

log = logging.getLogger(__name__)


class FakeHardware:
    def __init__(self):
        pass

    def setup(self):
        pass

    def led_on(self):
        pass

    def led_off(self):
        pass

    def button_state(self):
        return False


class Hardware:
    _BUTTON_PIN = 23
    _LED_PIN = 18

    def __init__(self):
        import RPi.GPIO as GPIO

    def setup(self):
        # Use Broadcom pin numbers (not Raspberry Pi pin numbers) for GPIO.
        GPIO.setmode(GPIO.BCM)

        # Enable LED and button (w/pull-up on latter).
        GPIO.setup(self._LED_PIN, GPIO.OUT)
        GPIO.setup(self._BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def led_on(self):
        GPIO.output(self._LED_PIN, GPIO.HIGH)

    def led_off(self):
        GPIO.output(self._LED_PIN, GPIO.LOW)

    def button_state(self):
        return GPIO.input(self._BUTTON_PIN)
