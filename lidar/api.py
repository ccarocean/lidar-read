import requests
import jwt
import datetime as dt
import struct
import os


def write_unsent(fname, num_meas, data):
    try:
        with open(fname, 'ab') as f:
            f.write(struct.pack('<H', num_meas) + data)
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

    print('Length of d:', len(d))
    if len(d) > 2:
        n = struct.unpack('<H', d[0:2])[0]
        print('Number of measurements:', n)
        ind = 2
        while ind + 6*n + 8 < len(d):
            print('Index:', ind)
            while not send(url, key, d[ind:ind+8+6*n]) and count < 100:
                count += 1
            if count == 100:
                print("woo")
                write_unsent(fname, n, d[ind:ind+8+6*n])
            ind = ind+8+6*n+2
            if ind >= len(d):
                break
            n = struct.unpack('<H', d[ind-2:ind])[0]
    print('number of measurements current:', num_meas)
    while not send(url, key, data) and count < 100:
        count += 1
    if count == 100:
        write_unsent(fname, num_meas, data)
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
