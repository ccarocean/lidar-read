import smbus


class Lidar:
    def __init__(self, address, led_pin):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.bus.write_data(self.address, 0x02, 0xff)
        self.bus.write_data(self.address, 0x04, 0x88)
        self.bus.write_data(self.address, 0x00, 0x04)
        self.countlist = []
        
    def read_meas(self):
        count = 0
        self.bus.write_byte_data(self.address, 0x00, 0x04)
        while self.bus.read_byte_data(self.address, 0x01) & 0x01:
            count += 1
        self.countlist.append(count)
        data = self.bus.read_i2c_block_data(self.address, 0x0f, 2)
        return (data[0] << 8) + data[1]
