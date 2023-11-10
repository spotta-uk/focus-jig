import time
import serial.tools.list_ports


def get_serial_connection():
    comport = find_comport()
    ser = serial.Serial(comport)
    ser.baudrate = 230400 * 4
    ser.timeout = 0.100  # 100ms timeout
    return ser


def find_comport():
    ports = serial.tools.list_ports.comports()
    comport = None
    for port in ports:
        # The UART has a specific vendor id (vid) and product id (pid)
        if port.vid == 1155 and port.pid == 14159:
            comport = port.device
            break
        if port.vid == 1027 and port.pid == 24577:
            comport = port.device
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
    return comport


def get_data(ser):
    while True:
        if ser.isOpen() is False:
            ser.open()
        raw = []
        ser.reset_input_buffer()
        print("Waiting for data", end="... ")
        start_time = time.time()
        while ser.in_waiting == 0 and ((time.time() - start_time) < 2.0):
            pass
        try:
            while True:
                read = ser.read(1)
                if len(read) != 1:
                    # Timeout
                    break
                raw.append(read)
                if len(raw) == 3:
                    # Check that the raw data start with the 3 byte sequence that all jpegs start with...
                    if raw != [b'\xff', b'\xd8', b'\xff']:
                        raw = []
        except Exception:
            ser.close()

        return raw
