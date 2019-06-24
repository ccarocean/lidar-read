import struct
import datetime as dt


def lidar_packet(dayhour, microseconds, measurements):
    # dayhour = dt.datetime(year, month, day, hour) IN UTC
    time_header = int((dayhour - dt.datetime(1970, 1, 1)).total_seconds())
    header = struct.pack('<q', time_header)
    data = b''
    for i, j in zip(microseconds, measurements):
        data = data + struct.pack('<LH', int(i), int(j))
    #data = [data + struct.pack('<LH', int(i), int(j)) for i, j in zip(microseconds, measurements)]
    print(data)
    return header + data
