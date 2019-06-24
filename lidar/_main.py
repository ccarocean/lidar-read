import datetime as dt
from queue import Queue
from threading import Thread
from .led import LED
from .packet import lidar_packet
from .collect import collect
from .api import send, sign


def read_key(fname):
    with open(fname, 'r') as f:
        key = f.read()
    return key


def main():
    led = LED(15)
    loc = 'harv'
    keys = {'harv': read_key('../../lidar/harv.key')}

    q = Queue()
    Thread(target=collect, args=(q,))

    url = 'https://cods.colorado.edu/api/gpslidar/lidar/' + loc

    try:
        while True:
            t_vec, meas_vec = [], []
            now = dt.datetime.utcnow()
            minute = dt.datetime(now.year, now.month, now.day, now.hour, now.minute)
            hour = dt.datetime(now.year, now.month, now.day, now.hour)
            while dt.datetime.utcnow() < (minute + dt.timedelta(minutes=1)):
                t, meas = q.get()
                meas_vec.append(meas)
                t_vec.append((t-hour).total_seconds() * 10**6)
                led.switch()
                q.task_done()
            # Get packet to send
            p = lidar_packet(hour, t_vec, meas_vec)
            # For now write to file - TODO: send API post
            while not send(url, keys[loc], p):
                pass

    finally:
        led.set_low()
