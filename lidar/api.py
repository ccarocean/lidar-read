import requests
import jwt
import datetime as dt
import struct
import os


def write_unsent(fname, l, data):
    try:
        with open(fname, 'ab') as f:
            f.write(struct.pack('<L', l) + data)
        return False
    except FileNotFoundError:
        print('Not Sent Directory does not exist. ')
        os._exit(1)


def call_send(url, key, data, num_meas):
    """ Function for sending packets. This is called in a separate thread to ensure all data is collected. This function
    runs until it receives a good code from the server. """
    count = 0
    fname = '/home/ccaruser/not-sent/lidar.bin'

    # Check if there is old unsent data
    with open(fname, 'r+b') as f:
        d = f.read()

    with open(fname, 'w') as f:
        f.write('')

    if len(d) > 4:
        ind = 4
        n = struct.unpack('<L', d[0:4])[0]
        while ind + n <= len(d):
            n = struct.unpack('<L', d[ind-4:ind])[0]
            while not send(url, key, d[ind:ind+n]) and count < 100:
                count += 1
            if count == 100:
                write_unsent(fname, n, d[ind:ind+n])
            ind = ind + n + 4

    while not send(url, key, data) and count < 100:
        count += 1
    if count == 100:
        write_unsent(fname, len(data), data)
        print("Failed Connection. Saved to " + fname)


def send(url, key, data):
    """ This function sends the packet to the web server. It returns true if it receives a 201 code, and false if
    it receives any other code. """
    headers = {"Content-Type": "application/octet-stream",  # Binary data
               "Bearer": sign(key)}  # Signature using private key
    try:
        upload = requests.post(url, data=data, headers=headers)  # Send API post request
    except:
        return False
    if upload.status_code != 201:
        return False
    print("Packet sent at", dt.datetime.utcnow())
    return True


def sign(key):
    """ Function for signing data using the private key for the given location. It uses the time to prevent denial of
    service replay attacks. """
    return jwt.encode({'t': str((dt.datetime.utcnow()-dt.datetime(1970, 1, 1)).total_seconds())}, key, algorithm='RS256')


def lidar_packet(dayhour, microseconds, measurements):
    """ This function creates the packet for sending the lidar data to the web server. """
    time_header = int((dayhour - dt.datetime(1970, 1, 1)).total_seconds())
    header = struct.pack('<q', time_header)  # Start with 64 bit unix time
    data = b''

    for i, j in zip(microseconds, measurements):
        if i > 0:
            data = data + struct.pack('<LH', int(i), int(j))  # pack each measurement
        else:
            print('Negative time:', i, j)
            os._exit(1)
    return header + data
