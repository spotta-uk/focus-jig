import time


class FactoryPcb:
    def __init__(self, io_expander, auto_turn_off_peripherals=True, quiet_mode=False):
        self.io_expander = io_expander
        self.auto_turn_off_peripherals = auto_turn_off_peripherals
        self.quiet_mode = quiet_mode

    def __del__(self):
        if self.auto_turn_off_peripherals:
            self.turn_off_all_peripherals()

    def start_state(self):
        self.turn_off_all_leds()
        self.io_expander.set_field("IODIR", 1, 0, 0x0)      # turn on start LED

    def wait_state(self):
        self.turn_off_all_leds()
        self.io_expander.set_field("IODIR", 1, 1, 0x0)      # turn on wait LED

    def fail_state(self):
        for i in range(9):
            self.turn_off_all_leds()
            self.buzzer_beep(time_secs=0.1)
            self.io_expander.set_field("IODIR", 1, 2, 0x0)  # turn on fail LED
            time.sleep(0.05)

    def pass_state(self):
        self.turn_off_all_leds()
        self.io_expander.set_field("IODIR", 1, 3, 0x0)  # turn on pass LED
        self.buzzer_beep(time_secs=0.15)

    def turn_off_all_leds(self):
        self.io_expander.set_field("IODIR", 4, 0, 0b1111)

    def turn_on_barcode_scanner(self):
        self.io_expander.set_field("IODIR", 1, 4, 0x0)

    def turn_off_barcode_scanner(self):
        self.io_expander.set_field("IODIR", 1, 4, 0x1)

    def turn_on_pod(self):
        self.io_expander.set_field("IODIR", 1, 5, 0x0)

    def turn_off_pod(self):
        self.io_expander.set_field("IODIR", 1, 5, 0x1)

    def power_cycle_pod(self, wait_off_time=0.1, wait_after_turn_on=0.1):
        self.turn_off_pod()
        time.sleep(wait_off_time)
        self.turn_on_pod()
        time.sleep(wait_after_turn_on)

    def buzzer_beep(self, time_secs=0.05):
        if not self.quiet_mode:
            self.io_expander.set_field("IODIR", 1, 6, 0x0)
            time.sleep(time_secs)
            self.io_expander.set_field("IODIR", 1, 6, 0x1)
        else:
            time.sleep(time_secs)

    def turn_off_all_peripherals(self):
        self.io_expander.write_reg("IODIR", 0xff)


class IOExpander:
    def __init__(self, stbridge, slave_addr):
        self.stbridge = stbridge
        self.slave_addr = slave_addr
        self.regs = {
            "IODIR"   : 0x00,
            "IPOL"    : 0x01,
            "GPINTEN" : 0x02,
            "DEFVAL"  : 0x03,
            "INTCON"  : 0x04,
            "IOCON"   : 0x05,
            "GPPU"    : 0x06,
            "INTF"    : 0x07,
            "INTCAP"  : 0x08,
            "GPIO"    : 0x09,
            "OLAT"    : 0x0A,
        }

    def read_reg(self, reg: [str, int]):
        if isinstance(reg, str):
            reg = self.regs[reg]
        self.stbridge.write_i2c(self.slave_addr, bytes([reg]))
        bytes_read = self.stbridge.read_i2c(self.slave_addr, 1)
        value = int.from_bytes(bytes_read, "big")
        return value

    def write_reg(self, reg: [str, int], value):
        if isinstance(reg, str):
            reg = self.regs[reg]
        self.stbridge.write_i2c(self.slave_addr, bytes([reg, value]))

    def set_field(self, reg, field_width, field_lsb_loc, field_value):
        mask = (0xff >> (8 - field_width)) << field_lsb_loc
        reg_value = self.read_reg(reg)
        new_reg_value = (reg_value & (~mask)) | field_value << field_lsb_loc
        self.write_reg(reg, new_reg_value)