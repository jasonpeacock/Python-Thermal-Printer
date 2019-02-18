# Python-Thermal-Printer

# Setup

## Raspberry Pi Software

### Update Packages

**Note:** The RPi.GPIO library for Python 2.7 is installed by default, to use Python 3.5 the `python3-rpi.gpio` library also needs to be installed.

```bash
# OS dependencies.
sudo apt-get update
sudo apt-get install \
    build-essential \
    cups \
    git \
    libcups2-dev \
    libcupsimage2-dev \
    python3-pip

# Python dependencies.
pip3 install \
    Pillow \
    RPi.GPIO \
    Unidecode \
    pyserial \
    python-twitter \
    wiringpi
```

### Install Printer Driver

```bash
cd ~
git clone https://github.com/adafruit/zj-58
cd zj-58
make
sudo ./install
```

### Configure Printer Driver

Generate a printer test page by holding down the feed button while connecting power.

Look for the baud rate that’s printed near the bottom of the page. This is typically either `9600` or `19200` baud - use the appropriate value in the first line:

```bash
sudo lpadmin -p ZJ-58 -E -v serial:/dev/serial0?baud=19200 -m zjiang/ZJ-58.ppd
sudo lpoptions -d ZJ-58
```

## Twitter

Uses Twitter 1.1 API application-only authentication. This **REQUIRES** a Twitter developer account and some account configuration.

Start at https://dev.twitter.com, sign in with your Twitter credentials, select "My Applications" from the avatar drop-down menu at the top right, then "Create a new application."

Provide a name, description, placeholder URL and complete the captcha, after which you'll be provided a `consumer key` and `consumer secret` for your app.

Copy these strings to the configuration file, and configure the search string to your liking.

**DO NOT SHARE your consumer key or secret!**

If you put code on Github or other public repository, replace them with dummy strings.
