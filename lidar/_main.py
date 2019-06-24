import datetime as dt
from queue import Queue
from threading import Thread
from .led import LED
from .packet import lidar_packet
from .collect import collect_data
from .api import send


def read_key(fname):
    with open(fname, 'r') as f:
        key = f.read()
    return key


def main():
    led = LED(15)

    led.switch()
    loc = 'harv'
    keys = {'harv': read_key('harv.key')}

    q = Queue()
    t = Thread(target=collect_data, args=(q,))
    t.start()

    #url = 'https://cods.colorado.edu/api/gpslidar/lidar/' + loc
    url = 'http://127.0.0.1:5000/lidar/' + loc

    try:
        while True:
            t_vec, meas_vec = [], []
            now = dt.datetime.utcnow()
            led_timer = now
            hour = dt.datetime(now.year, now.month, now.day, now.hour)
            minute = dt.datetime(now.year, now.month, now.day, now.hour, now.minute)
            end = minute + dt.timedelta(minutes=1)

            while dt.datetime.utcnow() < end:
                t, meas = q.get()
                print('Time:', t, ', Measurement:', meas)
                meas_vec.append(meas)
                t_vec.append((t-hour).total_seconds() * 10**6)
                if (dt.datetime.now() - led_timer).total_seconds() >= 1:
                    led.switch()
                    led_timer = dt.datetime.now()
                q.task_done()
            # Get packet to send
            print(meas_vec)
            p = lidar_packet(hour, t_vec, meas_vec)
            # Send API post

            print("Packet sending at", dt.datetime.utcnow())
            while not send(url, keys[loc], p):
                print('Issue sending packet.')

    finally:
        led.set_low()
