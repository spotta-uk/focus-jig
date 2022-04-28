#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This python script (focus_automated.py) only works on Linux PCs. Use focus.py for Windows PCs
Copyright Spotta Ltd. 2022
All rights reserved.
@author jordan.docker@spotta.co
"""

import serial.tools.list_ports
import cv2
import numpy as np
from pathlib import Path
from pystlink import PyStlink
from pods.pod import Pod
from stbridge import STBridge
from pcbs.factory_pcb import FactoryPcb, IOExpander

RX_WIDTH = 544
RX_HEIGHT = 480


def main():
    print("This python script (focus_automated.py) only works on Linux PCs. Use focus.py for Windows PCs")

    pystlink = PyStlink(verbosity=0)
    pod = Pod(pystlink)
    stbridge = STBridge()
    io_expander = IOExpander(stbridge, 0x20)
    factory_pcb = FactoryPcb(io_expander, quiet_mode=False)  # quiet_mode enable/disables buzzer sounds
    factory_pcb.turn_off_all_peripherals()

    ports = serial.tools.list_ports.comports()
    comport = None
    for port in ports:
        # The UART has a specific vendor id (vid) and product id (pid)
        if port.vid == 1027 and port.pid == 24577:
            comport = port.name
            break
    if comport is None:
        message = "Error: couldn't find COM port for UART\n"
        if len(ports) == 0:
            message += "No ports available"
        else:
            message += "Available ports...\n"
            for port in ports:
                message += f"{port.device} {port.description.ljust(35)} vid={port.vid} pid={port.pid} \n"
        raise Exception(message)
    ser = serial.Serial(comport)
    ser.baudrate = 230400*4
    ser.set_buffer_size(rx_size=256000, tx_size=12800)
    ser.timeout = 0.100  # 100ms timeout
    winname = "Spotta Focussing Program"
    cv2.destroyAllWindows()
    cv2.namedWindow(winname)
    cv2.moveWindow(winname, 0, 0)

    try:
        while True:
            if ser.isOpen() is False:
                ser.open()
            raw = []
            ser.reset_input_buffer()
            print("Waiting for data")
            ser.write("G".encode('ascii'))
            while ser.in_waiting == 0:
                ser.write("G".encode('ascii'))
            print("Data Received")
            try:
                for i in range(RX_WIDTH*RX_HEIGHT):
                    read = ser.read(1)
                    if len(read) != 1:
                        # Timeout
                        break
                    raw.append(read)
            except:
                ser.close()

            # We have received (presumably!) jpeg data
            print("Received " + str(len(raw)) + " bytes.")
            barray = bytes([int.from_bytes(x, "big") for x in raw])
            with open("img.jpeg", "wb+") as f:
                f.write(barray)
            # f = open("img.jpeg", "wb+")
            # f.write(barray)
            # f.close()
            img = cv2.imread("img.jpeg")
            if img is None:
                print("SYNC ERROR - SKIPPING FRAME!!")
                continue
            else:
                width = img.shape[1]
                height = img.shape[0]

                # Crop the image down to remove background
                # crop_top = int(height/14)
                # crop_left = int(width/8)
                # crop_right = width - crop_left
                # img = img[crop_top:, crop_left:crop_right, :]
                # width = img.shape[1]
                # height = img.shape[0]

                # Split the image into bands
                num_bands = 9
                band_height = int(height/num_bands)
                band_starts = [x*band_height for x in list(range(num_bands))]
                band_ends = [y*band_height for y in list(range(1, num_bands+1))]
                bands = [img[x[0]:x[1], :, :] for x in zip(band_starts, band_ends)]
                # https://www.pyimagesearch.com/2015/09/07/blur-detection-with-opencv/
                focus_coefficients = [cv2.Laplacian(cv2.cvtColor(x, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var() for x in bands]
                max_focus = max(float(3000), float(max(focus_coefficients)))
                focus_scale = [min([1.0, x/max_focus]) for x in focus_coefficients]
                overlay_colors = [(0, int(255*(x)), int(255*(1-x))) for x in focus_scale] # BGR
                # Make a bar chart of the focus position
                barchart_width = width
                barchart = np.zeros((height, barchart_width, 3), np.uint8)
                bar_sizes = [barchart_width*x for x in focus_scale]
                for i in range(num_bands):
                    bar = [np.array([[0, band_starts[i]], [bar_sizes[i], band_starts[i]], [bar_sizes[i], band_ends[i]], [0, band_ends[i]]], 'int32')]
                    cv2.fillPoly(barchart, bar, overlay_colors[i])
                    #cv2.putText(img, str(int(focus_coefficients[i])), (5, 25 + band_starts[i]), cv2.FONT_HERSHEY_SIMPLEX, 0.75, overlay_colors[i], 2)
                # Stitch the two images together
                stitched = np.concatenate((img, barchart), axis=1)
                # Draw a line for the target focus
                cv2.line(stitched, (0, height//2), (width + barchart_width, height//2), (255, 0, 0), 2)
                # Draw the arrow instructions box
                instructions = np.zeros((100, width + barchart_width, 3), np.uint8)
                color0 = (0, 255, 255)
                color1 = (255, 255, 0)
                cv2.ellipse(instructions, (50, 50), (25, 25), 90, 0, 270, color0, 2, cv2.LINE_AA)
                cv2.arrowedLine(instructions, (75, 50), (75, 51), color0, 2, cv2.LINE_AA, tipLength=10)
                cv2.arrowedLine(instructions, (100, 75), (100, 25), color0, 2, cv2.LINE_AA)
                cv2.ellipse(instructions, (250, 50), (25, 25), 90, 90, 360, color1, 2, cv2.LINE_AA)
                cv2.arrowedLine(instructions, (225, 50), (225, 51), color1, 2, cv2.LINE_AA, tipLength=10)
                cv2.arrowedLine(instructions, (300, 25), (300, 75), color1, 2, cv2.LINE_AA)
                # Stitch again
                stitched = np.concatenate((stitched, instructions), axis=0)
                cv2.imshow(winname, stitched)
                cv2.waitKey(25)

    except KeyboardInterrupt:
        ser.close()


if __name__ == "__main__":
    main()
