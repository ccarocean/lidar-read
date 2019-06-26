import datetime as dt
import sys
import argparse
from queue import Queue
from threading import Thread
from .led import LED
from .collect import collect_data
from .api import call_send, lidar_packet


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
    parser.add_argument('--led', type=int, default=15, help='LED pin. Default is 15. ')
    args = parser.parse_args()

    led = LED(args.led)  # initialize LED with pin 20

    led.switch()
    loc = args.location
    keys = {'harv': read_key('harv.key')}

    q = Queue()  # initialize queue for receiving lidar data
    t = Thread(target=collect_data, args=(q,))  # start thread for data collection
    t.start()

    # url = 'https://cods.colorado.edu/api/gpslidar/lidar/' + loc  # Web server location
    url = 'http://127.0.0.1:5000/lidar/' + loc

    next_meas, next_t = [], []

    led_timer = dt.datetime.utcnow()

    try:
        while True:
            t_vec, meas_vec = next_t, next_meas  # Initialize vectors
            now = dt.datetime.utcnow()
            hour = dt.datetime(now.year, now.month, now.day, now.hour)  # datetime of this hour
            minute = dt.datetime(now.year, now.month, now.day, now.hour, now.minute)  # datetime of this minute
            end = minute + dt.timedelta(minutes=1)  # end of current packet of data
            prev = 0
            next_t, next_meas = [], []
            # Take data until minute is over
            while dt.datetime.utcnow() < end:
                t, meas = q.get(timeout=2)  # Get data from queue
                if t.second >= prev:
                    meas_vec.append(meas)
                    t_vec.append((t-hour).total_seconds() * 10**6)  # Append microseconds since beginning of the hour
                    prev = t.second
                else:
                    hour = dt.datetime(t.year, t.month, t.day, t.hour)
                    next_t.append((t-hour).total_seconds() * 10**6)
                    next_meas.append(meas)
                    break
                if (dt.datetime.utcnow() - led_timer).total_seconds() >= 1:  # Switch lidar state every second
                    led.switch()
                    led_timer = dt.datetime.utcnow()
                q.task_done()

            # Put data in byte packet
            p = lidar_packet(hour, t_vec, meas_vec)

            # Send API post in thread
            print("Packet sending at", dt.datetime.utcnow())
            t2 = Thread(target=call_send, args=(url, keys[loc], p,))
            t2.start()

    finally:
        # Turn led off when program ends
        led.set_low()
