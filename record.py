#!/usr/bin/env python3

# pyinstaller ".\Focus Program\record.py" --onefile --noconsole
import serial.tools.list_ports
import cv2
from pathlib import Path
from datetime import datetime

RX_WIDTH = 544
RX_HEIGHT = 480

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
winname = "Pod Recorder"
cv2.destroyAllWindows()
cv2.namedWindow(winname)
cv2.moveWindow(winname, 0, 0)


output_dir = Path("output")
recording_dir = output_dir / f"{datetime.now().strftime('%Y-%m-%d--%H-%M-%S')}"
recording_dir.mkdir(parents=True, exist_ok=True)

img_num = 0

with ser:
    while True:
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
        output_file_path = recording_dir / f"{img_num}.jpeg"
        with open(output_file_path, "wb+") as f:
            f.write(barray)
        img = cv2.imread(str(output_file_path))
        if img is None:
            print("SYNC ERROR - SKIPPING FRAME!!")
            continue
        else:
            cv2.imshow(winname, img)
            k = cv2.waitKey(25)
            if k != -1:
                break

            img_num += 1
