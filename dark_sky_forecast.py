#!/usr/bin/env python3

# Weather forecast for Raspberry Pi w/Adafruit Mini Thermal Printer.
# Retrieves data from DarkSky.net's API, prints current conditions and
# forecasts for next two days.  See dark_sky_timetemp.py for a different
# weather example using nice bitmaps.
#
# Written by Adafruit Industries.  MIT license.
import attrdict
import calendar
import logging
import requests

from datetime import date, datetime

log = logging.getLogger(__name__)


class DarkSkyForecast:
    # Degree symbol on thermal printer.
    _DEG_SYMBOL = chr(0xF8)

    def __init__(self, *, printer, api_key, latitude, longitude):
        self._api_key = api_key
        self._latitude = latitude
        self._longitude = longitude
        self._printer = printer

    def update_and_print(self):

        url = (
            "https://api.darksky.net/forecast/"
            + self._api_key
            + "/"
            + self._latitude
            + ","
            + self._longitude
            + "?exclude=[alerts,minutely,hourly,flags]&units=us"
        )
        data = attrdict.AttrDict(requests.get(url).json())

        # Print heading
        self._printer.inverseOn()
        self._printer.print("{:^32}".format("DarkSky.Net Forecast"))
        self._printer.inverseOff()

        # Print current conditions
        self._printer.boldOn()
        self._printer.print("{:^32}".format("Current conditions:"))
        self._printer.boldOff()

        temp = data.currently.temperature
        cond = data.currently.summary
        self._printer.print("{}{}".format(temp, self._DEG_SYMBOL))
        self._printer.println(cond)
        self._printer.boldOn()

        # Print forecast
        self._printer.print("{:^32}".format("Forecast:"))
        self._printer.boldOff()
        self._forecast(data, 0)
        self._forecast(data, 1)

        self._printer.feed(3)

    # Dumps one forecast line to the printer
    def _forecast(self, data, idx):

        date = datetime.fromtimestamp(int(data.daily.data[idx].time))

        day = calendar.day_name[date.weekday()]
        temp_low = data.daily.data[idx].temperatureMin
        temp_high = data.daily.data[idx].temperatureMax
        cond = data.daily.data[idx].summary
        self._printer.print(
            "{}: low {}{} high {}{}".format(
                day, temp_low, self._DEG_SYMBOL, temp_high, self._DEG_SYMBOL
            )
        )

        # Convert pesky Unicode dash to standard ASCII.
        self._printer.println(cond.replace(u"\u2013", "-"))


if __name__ == "__main__":
    import argparse
    import sys

    import console_printer

    parser = argparse.ArgumentParser(description="Retrieve and print DarkSky.net forecast.")
    parser.add_argument("--api-key", required=True, help="The DarkSky.net API key.")
    parser.add_argument("--latitude", required=True, help="The forecast location latitude.")
    parser.add_argument("--longitude", required=True, help="The forecast location longitude.")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose DEBUG logging."
    )
    args = parser.parse_args()

    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG

    logging.basicConfig(format="[%(levelname)s]\t(%(name)s)\t%(message)s", level=log_level)

    log = logging.getLogger(__name__)

    forecast = DarkSkyForecast(
        api_key=args.api_key,
        latitude=args.latitude,
        longitude=args.longitude,
        printer=console_printer.ConsolePrinter(),
    )

    forecast.update_and_print()

    sys.exit(0)
