#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright Spotta Ltd. 2022
All rights reserved.
@author jordan.docker@spotta.co

This script can focus Forest Pod v5 and v6 boards (uses the red factory programming pcb and yellow sunrise pcb)
"""

from pathlib import Path
import jpeg_over_uart
import video_feed_window
import time
from pystlink import PyStlink
from stbridge import STBridge
from pcbs.factory_pcb import FactoryPcb, IOExpander


FOCUS_FIRMWARE = Path("forestpodv5-focus.srec")


def main():
    print("This python script only works on Linux PCs. Use focus.py for Windows PCs")
    pystlink = PyStlink(verbosity=0)
    stbridge = STBridge()
    io_expander = IOExpander(stbridge, 0x20)
    factory_pcb = FactoryPcb(io_expander, quiet_mode=False)  # quiet_mode enable/disables buzzer sounds
    factory_pcb.turn_off_all_peripherals()

    ser = jpeg_over_uart.get_serial_connection()
    video_feed_window.setup()

    factory_pcb.turn_on_pod()
    time.sleep(0.1)

    while True:
        raw = jpeg_over_uart.get_data(ser)
        if len(raw) == 0:
            print(f"\nPrograming pod with {FOCUS_FIRMWARE}")
            try:
                pystlink.program_flash(str(FOCUS_FIRMWARE))
                time.sleep(1.5)
            except Exception as e:
                pass
            continue
        video_feed_window.draw(raw)


if __name__ == "__main__":
    main()
