import datetime as dt
from queue import Queue
from threading import Thread
from .led import LED
from .packet import lidar_packet
from .collect import collect
from .api import send


def read_key(fname):
    with open(fname, 'r') as f:
        key = f.read()
    return key


def main():
    print('hi')
    led = LED(15)
    led.switch()
    loc = 'harv'
    keys = {'harv': read_key('harv.key')}

    q = Queue()
    Thread(target=collect, args=(q,))

    url = 'https://cods.colorado.edu/api/gpslidar/lidar/' + loc
    url = 'http://127.0.0.1:5000/lidar/' + loc

    try:
        while True:
            t_vec, meas_vec = [], []
            now = dt.datetime.utcnow()
            hour = dt.datetime(now.year, now.month, now.day, now.hour)
            min = dt.datetime(now.year, now.month, now.day, now.hour, now.minute)
            end = min + dt.timedelta(minutes=1)
            print('Now: ', now)
            print('End: ', end)

            while dt.datetime.utcnow() < end:
                print('Now: ', now)
                print('End: ', end)
                t, meas = q.get()
                meas_vec.append(meas)
                t_vec.append((t-hour).total_seconds() * 10**6)
                led.switch()
                q.task_done()
            # Get packet to send
            p = lidar_packet(hour, t_vec, meas_vec)
            # For now write to file - TODO: send API post
            while not send(url, keys[loc], p):
                print('attempt')

    finally:
        led.set_low()
