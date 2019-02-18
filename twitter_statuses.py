#!/usr/bin/env python3
#
# Uses Twitter 1.1 API application-only authentication.  This
# REQUIRES a Twitter account and some account configuration.  Start
# at dev.twitter.com, sign in with your Twitter credentials, select
# "My Applications" from the avatar drop-down menu at the top right,
# then "Create a new application."  Provide a name, description,
# placeholder URL and complete the captcha, after which you'll be
# provided a "consumer key" and "consumer secret" for your app.
# Copy these strings to the globals below, and configure the search
# string to your liking.  DO NOT SHARE your consumer key or secret!
# If you put code on Github or other public repository, replace them
# with dummy strings.

import logging
import twitter

from enum import Enum
from unidecode import unidecode

log = logging.getLogger(__name__)


class TwitterStatuses:
    class Printer:
        """Default STDOUT printer.

        Useful as a replacement when `Adafruit_Thermal` or other printers are not available.
        """

        def __init__(self):
            pass

        def print(self, content):
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

    class QueryResultType(Enum):
        MIXED = "mixed"
        POPULAR = "popular"
        RECENT = "recent"

    QUERY_MAX_RESULTS = 3
    QUERY_RESULT_TYPE = QueryResultType.RECENT

    def __init__(
        self, *, consumer_key, consumer_secret, query_string, last_id=0, printer=Printer()
    ):
        log.debug("Instantiating twitter client")

        self._query_string = query_string
        log.debug("Using query_string of [%s]", self._query_string)

        self._last_id = last_id
        log.debug("Using last_id of [%s]", self._last_id)

        self._printer = printer

        self._api = twitter.Api(
            consumer_key=consumer_key, consumer_secret=consumer_secret, application_only_auth=True
        )

    def update_and_print(self):
        log.debug("Querying twitter")

        statuses = self._api.GetSearch(
            count=self.QUERY_MAX_RESULTS,
            result_type=self.QUERY_RESULT_TYPE.value,
            since_id=self._last_id,
            term=self._query_string,
        )
        log.info("Retrieved [%s] statuses from twitter", len(statuses))

        for tweet in statuses:
            if tweet.id > self._last_id:
                self._last_id = tweet.id

            # Truncated tweets end in `...` and include a tiny-url Twitter link
            # to the full content which doesn't help when printed, so skip them.
            if tweet.truncated:
                log.warn("Skipping truncated tweet ID [%s]", tweet.id)
                continue

            log.debug("Printing tweet ID [%s]", tweet.id)
            self._printer.inverseOn()
            self._printer.print(" " + "{:<31}".format(tweet.user.screen_name))
            self._printer.inverseOff()

            self._printer.underlineOn()
            self._printer.print("{:<32}".format(tweet.created_at))
            self._printer.underlineOff()

            # Remap Unicode values to nearest ASCII equivalents when printing.
            self._printer.print(unidecode(tweet.text))

            self._printer.feed(3)

        return self._last_id


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Retrieve and print Twitter statuses.")
    parser.add_argument(
        "--query-string", required=True, help="The Twitter query string to search for tweets."
    )
    parser.add_argument(
        "--consumer-key", required=True, help="The Twitter API 'consumer key' value."
    )
    parser.add_argument(
        "--consumer-secret", required=True, help="The Twitter API 'consumer secret' value."
    )
    parser.add_argument(
        "--last-id", default=0, type=int, help="The ID of the last tweet printed."
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose DEBUG logging."
    )
    args = parser.parse_args()

    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG

    logging.basicConfig(format="[%(levelname)s]\t(%(name)s)\t%(message)s", level=log_level)

    log = logging.getLogger(__name__)

    twitter = TwitterStatuses(
        consumer_key=args.consumer_key,
        consumer_secret=args.consumer_secret,
        query_string=args.query_string,
        last_id=args.last_id,
    )

    last_id = twitter.update_and_print()
    log.info("Last status ID [%s]", last_id)

    sys.exit(0)
