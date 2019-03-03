import logging
import socket
import time

from PIL import Image

log = logging.getLogger(__name__)


class IotPrinter:
    """
    Manager the IoT printer.
    """

    # Duration for button hold (shutdown)
    _HOLD_TIME_SECONDS = 2

    # Debounce time for button taps
    _TAP_TIME_SECONDS = 0.01

    def __init__(self, *, printer, hardware, interval_seconds=30):
        self._interval_seconds = int(interval_seconds)
        self._next_interval = 0.0  # Time of next recurring operation
        self._daily_flag = False  # Set after daily trigger occurs

        self._printer = printer

        self._hardware = hardware

    def setup(self):
        # LED on while working.
        self._hardware.led_on()

        # Poll initial button state and time
        self._previous_button_state = self._hardware.button_state()
        self._previous_time = time.time()
        self._tap_enable = False
        self._hold_enable = False

        # Print greeting image
        self._printer.printImage(Image.open("./gfx/hello.png"), True)
        self._printer.feed(3)

        # Show IP address (if network is available)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 0))
            self._printer.print("My IP address is {}".format(s.getsockname()[0]))
            self._printer.feed(3)
        except:
            self._printer.boldOn()
            self._printer.println("Network is unreachable.")
            self._printer.boldOff()
            self._printer.print("Connect display and keyboard\n" "for network troubleshooting.")
            self._printer.feed(3)
            raise PrinterNetworkError("No internet connection")

        # Done working, LED off.
        self._hardware.led_off()

    def register_tasks_runners(
        self, *, run_daily_tasks, run_hold_tasks, run_interval_tasks, run_tap_tasks
    ):
        self._run_daily_tasks = run_daily_tasks
        self._run_hold_tasks = run_hold_tasks
        self._run_interval_tasks = run_interval_tasks
        self._run_tap_tasks = run_tap_tasks

    def run(self):
        while True:
            # Poll current button state and time
            buttonState = self._hardware.button_state()
            t = time.time()

            # Has button state changed?
            if buttonState != self._previous_button_state:
                self._previous_button_state = buttonState
                # Yes, save new state/time
                self._previous_time = t
            else:
                # Button state unchanged

                if (
                    t - self._previous_time
                ) >= self._HOLD_TIME_SECONDS:  # Button held more than 'HOLD_TIME_SECONDS'?
                    # Yes it has.  Is the hold action as-yet untriggered?
                    if self._hold_enable == True:  # Yep!
                        self._hold()  # Perform hold action (usu. shutdown)
                        self._hold_enable = False  # 1 shot...don't repeat hold action
                        self._tap_enable = False  # Don't do tap action on release
                elif (
                    t - self._previous_time
                ) >= self._TAP_TIME_SECONDS:  # Not HOLD_TIME_SECONDS.  TAP_TIME_SECONDS elapsed?
                    # Yes.  Debounced press or release...

                    # Button released?
                    if buttonState == True:
                        if self._tap_enable == True:  # Ignore if prior hold()
                            self._tap()  # Tap triggered (button released)
                            self._tap_enable = False
                            self._hold_enable = False
                    else:
                        # Button pressed
                        self._tap_enable = True
                        self._hold_enable = True

            # LED blinks while idle, for a brief interval every 2 seconds.
            # Pin 18 is PWM-capable and a "sleep throb" would be nice, but
            # the PWM-related library is a hassle for average users to install
            # right now.  Might return to this later when it's more accessible.
            if ((int(t) & 1) == 0) and ((t - int(t)) < 0.15):
                self._hardware.led_on()
            else:
                self._hardware.led_off()

            # Once per day (currently set for 6:30am local time, or when script
            # is first run, if after 6:30am), run forecast and sudoku scripts.
            l = time.localtime()
            if (60 * l.tm_hour + l.tm_min) > (60 * 6 + 30):
                if self._daily_flag == False:
                    self._daily()
                    self._daily_flag = True
            else:
                # Reset daily trigger
                self._daily_flag = False

            # Run interval scripts periodically.
            if t > self._next_interval:
                self._next_interval = t + self._interval_seconds
                self._interval()

    def _daily(self):
        """Called once per day (6:30am by default)."""
        self._hardware.led_on()

        log.debug("Running daily tasks")
        self._run_daily_tasks()

        self._hardware.led_off()

    def _hold(self):
        """Called when button is held down."""
        self._hardware.led_on()

        log.debug("Running hold tasks")
        self._run_hold_tasks()

        self._hardware.led_off()

    def _interval(self):
        """Called at periodic intervals."""
        self._hardware.led_on()

        log.debug("Running interval tasks")
        self._run_interval_tasks()

        self._hardware.led_off()

    def _tap(self):
        """Called when button is briefly tapped."""
        self._hardware.led_on()

        log.debug("Running tap tasks")
        self._run_tap_tasks()

        self._hardware.led_off()


class PrinterError(Exception):
    """Printer Error"""


class PrinterNetworkError(PrinterError):
    "Printer Network Error" ""
