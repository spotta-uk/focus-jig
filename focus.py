#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright Spotta Ltd. 2022
All rights reserved.
@author jordan.docker@spotta.co

This script can focus ForestPodv5 boards (uses the black development pcb and yellow sunrise pcb)
The forestpodv6-focus.srec firmware needs to be loaded up onto the pod prior to running this script
For a more automated solution use the focus_automated.py script (requires a linux pc and red factory programming pcb)
"""

import jpeg_over_uart
import video_feed_window


def main():
    ser = jpeg_over_uart.get_serial_connection()
    video_feed_window.setup()

    while True:
        raw = jpeg_over_uart.get_data(ser)
        video_feed_window.draw(raw)


if __name__ == "__main__":
    main()
