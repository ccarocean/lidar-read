import datetime as dt
import os
import socket
import argparse
from queue import Queue, Empty
from threading import Thread
import diskcache as dc
import logging
from .led import LED
from .collect import collect_data
from .api import call_send, lidar_packet, save_to_dc, send_old

logging.basicConfig(filename='/home/ccaruser/lidar.log', level=logging.INFO)


def read_key(fname):
    """ Read key for given location to sign data for sending over API link. """
    try:
        with open(fname, 'r') as f:
            key = f.read()
    except FileNotFoundError:
        logging.critical('Bad key location. ')
        os._exit(1)
    return key


def main():
    def_loc = socket.gethostname()[0:4]
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--location', type=str, default=def_loc,
                        help='GPS location. Default is first four letters of hostname (' + def_loc + ')')
    parser.add_argument('--led', type=int, default=20, help='LED pin. Default is 20.')
    args = parser.parse_args()

    led = LED(args.led)  # initialize LED
    led.set_high()

    loc = args.location
    key = read_key('/home/ccaruser/.keys/' + loc + '.key')

    q = Queue()  # initialize queue for receiving lidar data
    th = Thread(target=collect_data, args=(q,))  # start thread for data collection
    th.start()

    url = 'https://cods.colorado.edu/api/gpslidar/lidar/' + loc  # Web server location

    led_timer = dt.datetime.utcnow()

    t = None
    meas = None

    cache = dc.Cache('/var/tmp/unsent_lidar')

    t2 = Thread(target=send_old, args=(cache, url, key))
    t2.start()

    logging.info('Starting ' + loc + ' LiDAR at: ' + str(dt.datetime.utcnow()))

    try:
        while True:
            t_vec, meas_vec = [], []  # Initialize vectors
            now = dt.datetime.utcnow()
            hour = dt.datetime(now.year, now.month, now.day, now.hour)  # datetime of this hour
            minute = dt.datetime(now.year, now.month, now.day, now.hour, now.minute)  # datetime of this minute
            end = minute + dt.timedelta(minutes=1)  # end of current packet of data
            # Take data until minute is over
            if not t:
                try:
                    t, meas = q.get(timeout=3)  # Get data from queue
                except Empty:
                    logging.warning('Queue Empty (Why?)')
            while t < end:
                meas_vec.append(meas)
                t_vec.append((t-hour).total_seconds() * 10**6)  # Append microseconds since beginning of the hour
                if (dt.datetime.utcnow() - led_timer).total_seconds() >= 1:  # Switch led state every second
                    led.switch()
                    led_timer = dt.datetime.utcnow()
                try:
                    q.task_done()
                    t, meas = q.get(timeout=3)  # Get data from queue
                except Empty:
                    logging.critical('Queue Empty (Why?)')

            # Put data in byte packet
            p = lidar_packet(hour, t_vec, meas_vec)

            # Send API post in thread
            if not t2.isAlive():
                t2 = Thread(target=call_send, args=(url, key, p, (hour-dt.datetime(1970, 1, 1)).total_seconds() + t_vec[0],
                                                    cache))
                t2.start()
            else:
                save_to_dc(cache, (hour-dt.datetime(1970, 1, 1)).total_seconds() + t_vec[0], p)

    finally:
        # Turn led off when program ends
        led.set_low()
