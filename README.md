# Python-Thermal-Printer

# Raspberry Pi Software Setup

## Update Packages

**Note:** The RPi.GPIO library for Python 2.7 is installed by default, to use Python 3.5 the `python3-rpi.gpio` library also needs to be installed.

```bash
sudo apt-get update
sudo apt-get install \
    build-essential \
    cups \
    git \
    libcups2-dev \
    libcupsimage2-dev \
    python3-pil \
    python3-serial \
    python3-unidecode \
    python3-rpi.gpio \
    wiringpi
```

## Install Printer Driver

```bash
cd ~
git clone https://github.com/adafruit/zj-58
cd zj-58
make
sudo ./install
```

## Configure Printer Driver

Generate a printer test page by holding down the feed button while connecting power.

Look for the baud rate that’s printed near the bottom of the page. This is typically either `9600` or `19200` baud - use the appropriate value in the first line:

```bash
sudo lpadmin -p ZJ-58 -E -v serial:/dev/serial0?baud=19200 -m zjiang/ZJ-58.ppd
sudo lpoptions -d ZJ-58
```
