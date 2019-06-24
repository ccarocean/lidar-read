import datetime as dt
import time
from lidar import Lidar


def collect(q):
    lid = Lidar(1, 0x62)
    while True:
        t = dt.datetime.utcnow()
        meas = lid.read_meas()
        q.put_nowait((t, meas))
        time.sleep(max((0.005 - (dt.datetime.utcnow() - t).total_seconds(), 0)))
