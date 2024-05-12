import machine, utime  # type: ignore pi pico specific imports


class MCP9808:
    def __init__(self):
        sda = machine.Pin(0)
        scl = machine.Pin(1)
        self.adr = 0x18  # 24
        self.i2c = machine.I2C(0, sda=sda, scl=scl, freq=400_000)
        self.led = machine.Pin("LED", machine.Pin.OUT)
        if not self.i2c.scan():
            self.led.value(1)
            utime.sleep(0.5)
            self.led.value(0)
            self.led.value(1)
            utime.sleep(0.5)
            self.led.value(0)
            raise Exception("No i2c device")

        self.__read_config()

    def set_resolution(self):
        # currently not working
        # 00 = +0.5°C (tCONV = 30 ms typical)
        # 01 = +0.25°C (tCONV = 65 ms typical)
        # 10 = +0.125°C (tCONV = 130 ms typical)
        # 11 = +0.0625°C (power-up default, t CONV = 250 ms typical)
        self.i2c.writeto_mem(
            self.adr, 0x08, bytes(0x03)
        )  # address, resolution register, accuracy

    def __read_config(self):
        self.config = self.i2c.readfrom_mem(
            self.adr, 0x01, 2
        )  # reads config register of 2 bytes

    def __write_config(self):
        if isinstance(self.config, bytes) and len(self.config) == 2:
            self.i2c.writeto_mem(self.adr, 0x01, self.config)
        else:
            raise Exception("Wrong config format")

    def power_change(self, change):
        first_byte = self.config[0]
        if change == "on":  # change to 0
            modified_byte = first_byte & 0b11111110
        elif change == "off":  # change to 1
            modified_byte = first_byte | 0b00000001
        elif change == "toggle":
            modified_byte = first_byte ^ 0b00000001
        else:
            raise Exception("Wrong power_change command")
        self.config = bytes(modified_byte, self.config[1])
        self.__write_config()

    def read_temp(self):
        try:
            data = self.i2c.readfrom_mem(self.adr, 0x05, 2)
            self.led.value(0)
            # Convert the data to 13-bits
            ctemp: float = ((data[0] & 0x1F) * 256) + data[1]
            if ctemp > 4095:
                ctemp -= 8192
            ctemp = ctemp * 0.0625
            return ctemp
        except:
            self.led.value(1)
            raise Exception("Device disconnected")
            # machine.reset()
