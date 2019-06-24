import struct
import datetime as dt


def lidar_packet(dayhour, microseconds, measurements):
    time_header = int((dayhour - dt.datetime(1970, 1, 1)).total_seconds())
    header = struct.pack('<q', time_header)
    data = b''
    for i, j in zip(microseconds, measurements):
        data = data + struct.pack('<LH', int(i), int(j))
    return header + data
