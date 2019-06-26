import requests
import jwt
import datetime as dt
import struct
import sys


def call_send(url, key, data):
    """ Function for sending packets. This is called in a separate thread to ensure all data is collected. This function
    runs until it receives a good code from the server. """
    count = 0
    fname = '/home/ccaruser/not-sent/lidar.bin'
    while not send(url, key, data) and count < 100:
        count += 1
    if count == 100:
        try:
            with open(fname, 'a+') as f:
                f.write(data)
            print("Failed Connection. Saved to " + fname)
        except FileNotFoundError:
            print('Not Sent Directory does not exist. ')
            sys.exit(0)


def send(url, key, data):
    """ This function sends the packet to the web server. It returns true if it receives a 201 code, and false if
    it receives any other code. """
    headers = {"Content-Type": "application/octet-stream",  # Binary data
               "Bearer": sign(key)}  # Signature using private key
    try:
        upload = requests.post(url, data=data, headers=headers)  # Send API post request
    except ConnectionError:
        return False
    if upload.status_code != 201:
        return False
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
        data = data + struct.pack('<LH', int(i), int(j))  # pack each measurement
    return header + data
