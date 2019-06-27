import datetime as dt
import os
import struct
import sys


def save_lidar(data, data_directory, loc):
    """ Function for saving lidar data from API. """
    if len(data) < 8:
        print("No data in LiDAR packet. ")
        return
    unix_time = struct.unpack('<q', data[0:8])[0]  # First thing is unix time
    print(unix_time)
     # Find day and hour
    dayhour = dt.datetime(1970, 1, 1) + dt.timedelta(seconds=unix_time)
    print(dayhour)
    tvec, measvec = [], []  # Initialization
    num = (len(data)-8)/6  # Number of measurements
    for i in range(int(num)):
        t, meas = struct.unpack('<LH', data[8+i*6:8+(i+1)*6])  # Unpack data
        tvec.append(dayhour + dt.timedelta(microseconds=t))
        measvec.append(meas)
    try:
        with open(os.path.join(data_directory, loc, 'lidar', dayhour.strftime('%Y-%m-%d.txt')), 'a+') as f:
            for i, j in zip(tvec, measvec):
                f.write(f'{i} {j}\n')
    except FileNotFoundError:
        print("Data directory is bad. Try again. ")
        sys.exit(0)
