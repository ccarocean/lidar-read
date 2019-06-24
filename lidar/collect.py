import datetime as dt
import time
from .connect import Lidar


def collect_data(q):
    lid = Lidar(0x62)
    while True:
        t = dt.datetime.utcnow()
        meas = lid.read_meas()
        q.put_nowait((t, meas))
        time.sleep(max((0.005 - (dt.datetime.utcnow() - t).total_seconds(), 0)))
