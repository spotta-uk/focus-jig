#!/usr/bin/env bash

# This script should be run in the home directory as sudo 

rules='# STLINK-V2
SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="3748", MODE="0666"
# STLINK-V3
SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="374f", MODE="0666"'

apt update
apt upgrade -y
apt install -y python3.12 python3-pip python3.12-venv
apt install -y libboost-python-dev libfmt-dev libusb-1.0-0-dev

echo -n "$rules" > "/etc/udev/rules.d/90-spotta-stlink.rules"
udevadm control --reload
usermod -a -G dialout $SUDO_USER

sudo -u $SUDO_USER python3 -m venv venv
source venv/bin/activate
pip3 install setuptools
pip3 install -r requirements_linux.txt

echo
echo
echo "-----------------------------------------"
echo "A reboot and disconnect/reconnect the stlink might be required to sort out the usb permissions. Then try running... venv/bin/python3 focus_automated_LINUX_ONLY.py --board bedpodv11"
echo "-----------------------------------------"


