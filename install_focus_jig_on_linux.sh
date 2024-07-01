#!/usr/bin/env bash

# This script should be run in the home directory

rules='# STLINK-V2
SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="3748", MODE="0666"
# STLINK-V3
SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="374f", MODE="0666"'

sudo apt update
sudo apt upgrade
sudo apt install -y git python3.12 python3-pip python3.12-venv

cd ~
mkdir repos
cd repos
git clone https://github.com/spotta-smart-pest-systems/pystlink.git
echo -n "$rules" > "/etc/udev/rules.d/90-spotta-stlink.rules"
sudo udevadm control --reload
git clone --recursive https://github.com/spotta-smart-pest-systems/stbridge.git
sudo apt install -y make libboost-python-dev libfmt-dev libusb-1.0-0-dev
cd ~/repos/stbridge
make


cd ~/repos/focus_jig
pip install setuptools
python3 -m venv venv
source venv/bin/activate
pip install ../stbridge
pip install ../pystlink
pip install -r requirements_linux.txt <- get numpy 1.26.4

echo "A reboot and removing and reinserting the stlink might be required to sort out the usb permissions"
# python3 focus_automated_LINUX_ONLY.py --board bedpodv11

