from textwrap import wrap


class Pod:
    def __init__(self, pystlink):
        self.pystlink = pystlink

    def program_firmware(self, firmware_path):
        self.pystlink.program_flash(str(firmware_path))

    def read_uid(self):
        # Read the UID of the MCU (96-bit UID)
        # Base address: 0x1FFF 7590
        # Address offset range: 0x00 to 0x0B (12 bytes)
        words = self.pystlink.read_words(0x1FFF7590, 3)
        uid = "".join(words).upper()
        return uid

    def read_device_family(self):
        # Read the ID Code
        # Base address 0xE004 2000
        # 4 bytes to read
        id_code = self.pystlink.read_word(0xE0042000)[-3:]
        if id_code == "461":
            device_family = "STM32L496xx/4A6xx"
        elif id_code == "415":
            device_family = "STM32L475xx/476xx/486xx"
        elif id_code == "470":
            device_family = "STM32L4Rxxx/Sxxx"
        else:
            device_family = "unknown device family"
        return device_family

    def connected(self):
        target_voltage = self.pystlink.get_target_voltage()
        # print(f"{target_voltage} Volts")
        return target_voltage > 3.1

    def program_credentials_to_otp(self, credentials):
        block_start = 0x1FFF7000
        errors = 0
        if credentials.activation_method() == "OTAA-1.0.2":
            errors += self.pystlink.program_otp(block_start + 0x00, reverse_bytes_in_words(credentials.dev_eui()))    # LORAWAN_DEVICE_EUI
            errors += self.pystlink.program_otp(block_start + 0x08, reverse_bytes_in_words(credentials.app_eui()))    # LORAWAN_JOIN_EUI
            errors += self.pystlink.program_otp(block_start + 0x10, reverse_bytes_in_words(credentials.app_key()))    # LORAWAN_APP_KEY (OTAA)
        elif credentials.activation_method() == "ABP-1.0.2":
            errors += self.pystlink.program_otp(block_start + 0x00, reverse_bytes_in_words(credentials.dev_eui()))    # LORAWAN_DEVICE_EUI
            errors += self.pystlink.program_otp(block_start + 0x08, reverse_bytes_in_words(credentials.app_eui()))    # LORAWAN_JOIN_EUI
            errors += self.pystlink.program_otp(block_start + 0x40, reverse_bytes_in_words(credentials.nwk_s_key()))  # LORAWAN_F_NWK_S_INT_KEY
            errors += self.pystlink.program_otp(block_start + 0x50, reverse_bytes_in_words(credentials.nwk_s_key()))  # LORAWAN_S_NWK_S_INT_KEY
            errors += self.pystlink.program_otp(block_start + 0x60, reverse_bytes_in_words(credentials.nwk_s_key()))  # LORAWAN_NWK_S_ENC_KEY
            errors += self.pystlink.program_otp(block_start + 0x70, reverse_bytes_in_words(credentials.app_s_key()))  # LORAWAN_APP_S_KEY
            errors += self.pystlink.program_otp(block_start + 0x80, credentials.dev_addr() + "ffffffff")              # LORAWAN_DEVICE_ADDRESS
        else:
            print("Activation Method of assigned credentials is not recognised. Ask for help.")
            return False
        return errors == 0


def reverse_bytes_in_words(value):
    output = ""
    words = wrap(value, 8)
    for word in words:
        hex_bytes = wrap(word, 2)
        hex_bytes.reverse()
        output += "".join(hex_bytes)
    return output