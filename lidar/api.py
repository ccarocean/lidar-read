import requests
import jwt
import datetime as dt
import struct
import os


def save_old(url, key):
    fname = '/home/ccaruser/not-sent/lidar.bin'
    with open(fname, 'r+b') as f:
        data = f.read()
        f.seek(0)

    with open(fname, 'w') as f:
        f.write('')

    if len(data) < 2:
        return

    n = struct.unpack('<H', data[0:2])[0]
    count = 2
    while count + 6*n + 8 < len(data):
        call_send(url, key, data[count:count+8+6*n], n)
        count = count+8+6*n+2
        if count >= len(data):
            break
        n = struct.unpack('<H', data[count-2:count])[0]

    f.truncate()


def call_send(url, key, data, num_meas):
    """ Function for sending packets. This is called in a separate thread to ensure all data is collected. This function
    runs until it receives a good code from the server. """
    count = 0
    fname = '/home/ccaruser/not-sent/lidar.bin'
    while not send(url, key, data) and count < 100:
        count += 1
    if count == 100:
        try:
            with open(fname, 'a+b') as f:
                f.write(struct.pack('<H', num_meas) + data + b'\n')
            print("Failed Connection. Saved to " + fname)
            return False
        except FileNotFoundError:
            print('Not Sent Directory does not exist. ')
            os._exit(1)
    print("Packet sent at", dt.datetime.utcnow())
    return True


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
