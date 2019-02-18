#!/usr/bin/env python3

# Main script for Adafruit Internet of Things Printer 2.  Monitors button
# for taps and holds, performs periodic actions (Twitter polling by default)
# and daily actions (Sudoku and weather by default).
#
# Written by Adafruit Industries.  MIT license.
#
# MUST BE RUN AS ROOT (due to GPIO access)
#
# Required software includes Adafruit_Thermal, Python Imaging, and PySerial
# libraries. Other libraries used are part of stock Python install.
#
# Resources:
# http://www.adafruit.com/products/597 Mini Thermal Receipt Printer
# http://www.adafruit.com/products/600 Printer starter pack

import Adafruit_Thermal
import RPi.GPIO as GPIO
import socket
import subprocess
import time

import .twitter_statuses

from PIL import Image

log = logging.getLogger(__name__)

class Printer:

    _LED_PIN = 18
    _BUTTON_PIN = 23
    _HOLD_TIME_SECONDS = 2  # Duration for button hold (shutdown)
    _TAP_TIME_SECONDS = 0.01  # Debounce time for button taps

    def __init__(self, *, serial_device, baud_rate, timeout_seconds):
        self._next_interval = 0.0  # Time of next recurring operation
        self._daily_flag = False  # Set after daily trigger occurs
        self._last_id = "1"  # State information passed to/from interval script

        self._printer = Adafruit_Thermal(serial_device, baud_rate, timeout=timeout_seconds)

        # Use Broadcom pin numbers (not Raspberry Pi pin numbers) for GPIO.
        GPIO.setmode(GPIO.BCM)

        # Enable LED and button (w/pull-up on latter).
        GPIO.setup(self._LED_PIN, GPIO.OUT)
        GPIO.setup(self._BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # LED on while working.
        GPIO.output(self._LED_PIN, GPIO.HIGH)

        self._twitter = TwitterStatuses(
            consumer_key=args.consumer_key,
            consumer_secret=args.consumer_secret,
            query_string=args.query_string,
            last_id=args.last_id,
        )

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
            # XXX raise exception instead
            exit(0)

        # Print greeting image
        self._printer.printImage(Image.open("./gfx/hello.png"), True)
        self._printer.feed(3)
        GPIO.output(self._LED_PIN, GPIO.LOW)

        # Poll initial button state and time
        previous_button_state = GPIO.input(self._BUTTON_PIN)
        previous_time = time.time()
        tap_enable = False
        hold_enable = False

    def run(self):
        while True:
            # Poll current button state and time
            buttonState = GPIO.input(self._BUTTON_PIN)
            t = time.time()

            # Has button state changed?
            if buttonState != previous_button_state:
                previous_button_state = buttonState  # Yes, save new state/time
                previous_time = t
            else:  # Button state unchanged
                if (t - previous_time) >= self._HOLD_TIME_SECONDS:  # Button held more than 'HOLD_TIME_SECONDS'?
                    # Yes it has.  Is the hold action as-yet untriggered?
                    if hold_enable == True:  # Yep!
                        hold()  # Perform hold action (usu. shutdown)
                        hold_enable = False  # 1 shot...don't repeat hold action
                        tap_enable = False  # Don't do tap action on release
                elif (
                    t - previous_time
                ) >= self._TAP_TIME_SECONDS:  # Not HOLD_TIME_SECONDS.  TAP_TIME_SECONDS elapsed?
                    # Yes.  Debounced press or release...
                    if buttonState == True:  # Button released?
                        if tap_enable == True:  # Ignore if prior hold()
                            tap()  # Tap triggered (button released)
                            tap_enable = False  # Disable tap and hold
                            hold_enable = False
                    else:  # Button pressed
                        tap_enable = True  # Enable tap and hold actions
                        hold_enable = True

            # LED blinks while idle, for a brief interval every 2 seconds.
            # Pin 18 is PWM-capable and a "sleep throb" would be nice, but
            # the PWM-related library is a hassle for average users to install
            # right now.  Might return to this later when it's more accessible.
            if ((int(t) & 1) == 0) and ((t - int(t)) < 0.15):
                GPIO.output(self._LED_PIN, GPIO.HIGH)
            else:
                GPIO.output(self._LED_PIN, GPIO.LOW)

            # Once per day (currently set for 6:30am local time, or when script
            # is first run, if after 6:30am), run forecast and sudoku scripts.
            l = time.localtime()
            if (60 * l.tm_hour + l.tm_min) > (60 * 6 + 30):
                if daily_flag == False:
                    daily()
                    daily_flag = True
            else:
                daily_flag = False  # Reset daily trigger

            # Every 30 seconds, run Twitter scripts.  'last_id' is passed around
            # to preserve state between invocations.  Probably simpler to do an
            # import thing.
            if t > next_interval:
                next_interval = t + 30.0
                result = interval()
                if result is not None:
                    last_id = result.decode("utf-8").rstrip("\r\n")

    def _tap(self):
        """Called when button is briefly tapped. Invokes time/temperature script."""
        GPIO.output(self._LED_PIN, GPIO.HIGH)  # LED on while working
        subprocess.call(["./timetemp.py"])
        GPIO.output(self._LED_PIN, GPIO.LOW)


    def _hold(self):
        """Called when button is held down. Prints image, invokes shutdown process."""
        GPIO.output(self._LED_PIN, GPIO.HIGH)
        self._printer.printImage(Image.open("gfx/goodbye.png"), True)
        self._printer.feed(3)
        subprocess.call("sync")
        subprocess.call(["shutdown", "-h", "now"])
        GPIO.output(self._LED_PIN, GPIO.LOW)


    def _interval(self):
        """Called at periodic intervals (30 seconds by default)."""
        GPIO.output(self._LED_PIN, GPIO.HIGH)

        last_id = self._twitter.update_and_print()
        log.info("Last status ID [%s]", last_id)

        GPIO.output(self._LED_PIN, GPIO.LOW)

        return last_id


    def _daily(self):
        """Called once per day (6:30am by default). Invokes weather forecast and sudoku-gfx scripts."""
        GPIO.output(self._LED_PIN, GPIO.HIGH)
        subprocess.call(["./forecast.py"])
        subprocess.call(["./sudoku-gfx.py"])
        GPIO.output(self._LED_PIN, GPIO.LOW)

