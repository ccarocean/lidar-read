import datetime as dt
import sys
import argparse
from queue import Queue
from threading import Thread
from .led import LED
from .collect import collect_data
from .api import call_send, lidar_packet, save_old


def read_key(fname):
    """ Read key for given location to sign data for sending over API link. """
    try:
        with open(fname, 'r') as f:
            key = f.read()
    except FileNotFoundError:
        print('Bad key location. ')
        sys.exit(0)
    return key


def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--location', type=str, default='harv', help='GPS location. Default is harv.')
    parser.add_argument('--led', type=int, default=21, help='LED pin. Default is 21. ')
    args = parser.parse_args()

    led = LED(args.led)  # initialize LED with pin 20

    led.switch()
    loc = args.location
    keys = {'harv': read_key('harv.key')}

    q = Queue()  # initialize queue for receiving lidar data
    th = Thread(target=collect_data, args=(q,))  # start thread for data collection
    th.start()

    # url = 'https://cods.colorado.edu/api/gpslidar/lidar/' + loc  # Web server location
    url = 'http://127.0.0.1:5000/lidar/' + loc

    led_timer = dt.datetime.utcnow()

    t = None
    meas = None

    try:
        while True:
            t_vec, meas_vec = [], []  # Initialize vectors
            now = dt.datetime.utcnow()
            hour = dt.datetime(now.year, now.month, now.day, now.hour)  # datetime of this hour
            minute = dt.datetime(now.year, now.month, now.day, now.hour, now.minute)  # datetime of this minute
            end = minute + dt.timedelta(minutes=1)  # end of current packet of data
            # Take data until minute is over
            if not t:
                t, meas = q.get(timeout=1)  # Get data from queue
            while t < end:
                meas_vec.append(meas)
                t_vec.append((t-hour).total_seconds() * 10**6)  # Append microseconds since beginning of the hour
                if (dt.datetime.utcnow() - led_timer).total_seconds() >= 1:  # Switch led state every second
                    led.switch()
                    led_timer = dt.datetime.utcnow()
                q.task_done()
                t, meas = q.get(timeout=1)  # Get data from queue

            # Put data in byte packet
            p = lidar_packet(hour, t_vec, meas_vec)

            # Send API post in thread
            print("Packet sending at", dt.datetime.utcnow())
            t2 = Thread(target=call_send, args=(url, keys[loc], p,))
            t2.start()
            t3 = Thread(target=save_old, args=(url, keys[loc]))
            t3.start()
            print("Packet sending at", dt.datetime.utcnow())

    finally:
        # Turn led off when program ends
        led.set_low()
