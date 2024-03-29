from queue import Queue
from threading import Thread
import datetime as dt
import time
import smbus


# This is a testing script for receiving lidar data and displaying it to the screen.

class Lidar:
    def __init__(self, address):
        self.bus = smbus.SMBus(1)
        self.address = address
        if self.bus.read_byte_data(self.address, 0x02) != 0xff:
            self.bus.write_byte_data(self.address, 0x02, 0xff)
        if self.bus.read_byte_data(self.address, 0x04) != 0x80:
            self.bus.write_byte_data(self.address, 0x04, 0x80)
        self.bus.write_byte_data(self.address, 0x00, 0x04)

    def read_meas(self):
        self.bus.write_byte_data(self.address, 0x00, 0x04)
        while self.bus.read_byte_data(self.address, 0x01) & 0x01:
            pass
        data = self.bus.read_i2c_block_data(self.address, 0x0f, 2)
        health = self.bus.read_i2c_block_data(self.address, 0x01, 1)
        return ((data[0] << 8) + data[1], health[0] & 0x3F)


def collect_data(q):
    lid = Lidar(0x62)
    while True:
        t = dt.datetime.utcnow()
        meas, health = lid.read_meas()
        if (health == 0x3E or health == 0x3A) and meas > 1:
            q.put_nowait((t, meas, health))
            time.sleep(max((0.005 - (dt.datetime.utcnow() - t).total_seconds(), 0)))


q = Queue()
t = Thread(target=collect_data, args=(q,))
t.start()

while True:
    t, meas, health = q.get()
    print('Time:', t, ', Measurement:', meas, 'Health:', hex(health))
    q.task_done()
