import datetime as dt
import time
import smbus


class Lidar:
    """ Class for connecting with, configuring, and reading data from a Garmin LIDAR-Lite v3HP. """
    def __init__(self, address):
        self.bus = smbus.SMBus(1)  # Using the first I2C bus
        self.address = address  # Lidar address
        if self.bus.read_byte_data(self.address, 0x02) != 0xff:
            # Set maximum acquisition count to highest value to hopefully allow for the highest possible accuracy
            self.bus.write_byte_data(self.address, 0x02, 0xff)
        if self.bus.read_byte_data(self.address, 0x04) != 0x08:
            # Turn on quick termination to speed up rate
            self.bus.write_byte_data(self.address, 0x04, 0x08)
        # Ask for first measurement from LiDAR
        self.bus.write_byte_data(self.address, 0x00, 0x04)

    def read_meas(self):
        self.bus.write_byte_data(self.address, 0x00, 0x04)  # Ask for LiDAR measurement
        while self.bus.read_byte_data(self.address, 0x01) & 0x01:  # wait for LSB to go low
            pass
        data = self.bus.read_i2c_block_data(self.address, 0x0f, 2)  # Read measurement
        health = self.bus.read_i2c_block_data(self.address, 0x01, 1)
        return ((data[0] << 8) + data[1], health[0] & 0x3F)


def collect_data(q):
    lid = Lidar(0x62)  # Initialize lidar with address 0x62
    while True:
        t = dt.datetime.utcnow()
        meas, health = lid.read_meas()  # Read LiDAR measurement
        if (health == 0x3E or health == 0x3A) and meas > 1 and meas < 1000:
            q.put_nowait((t, meas))
            time.sleep(max((0.005 - (dt.datetime.utcnow() - t).total_seconds(), 0)))  # Sleep to get rate near 200Hz
