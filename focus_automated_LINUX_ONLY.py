#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright Spotta Ltd. 2022
All rights reserved.
@author jordan.docker@spotta.co

"""
from pathlib import Path
import jpeg_over_uart
import video_feed_window
import time
import argparse
import sys
import subprocess
from stbridge import STBridge
from pcbs.factory_pcb import FactoryPcb, IOExpander

parser = argparse.ArgumentParser(description="This script can focus bedpod and forestpod boards (uses the red factory programming pcb and yellow sunrise pcb)")

parser.add_argument("--board",type=str,help="board to program and run focus jig application on")
args = parser.parse_args()


def program_flash(binary_file):
   PYOCD_EXE = Path("venv/bin")/ "pyocd"
   subprocess.run([PYOCD_EXE,"load","-e", "chip","--frequency","4000khz","--target","stm32l496vgtx","-a",
                    "0x08000000","--format","bin",binary_file])
   subprocess.run([PYOCD_EXE,"reset","--target","stm32l496vgtx"])

def main():
    
    FOCUS_FIRMWARE = Path("bin")/ (args.board + "-focus.bin")

    if not FOCUS_FIRMWARE.is_file():
        print("\033[91m Error:\033[0m File "+str(FOCUS_FIRMWARE) + " was not found!")
        sys.exit()

    print("This python script only works on Linux PCs. Use focus.py for Windows PCs")

    stbridge = STBridge()
    io_expander = IOExpander(stbridge, 0x20)
    factory_pcb = FactoryPcb(io_expander, quiet_mode=False)  # quiet_mode enable/disables buzzer sounds
    factory_pcb.turn_off_all_peripherals()

    ser = jpeg_over_uart.get_serial_connection()
    video_feed_window.setup()
    factory_pcb.turn_on_pod()
    time.sleep(1)
    
    while True:
        raw = jpeg_over_uart.get_data(ser)
        if len(raw) == 0:
            print(f"\nPrograming pod with {FOCUS_FIRMWARE}")
            try:
                program_flash(FOCUS_FIRMWARE)
                time.sleep(3)
            except Exception as e:
                pass
            continue
        video_feed_window.draw(raw)

if __name__ == "__main__":
    main()