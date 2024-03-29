import requests
import jwt
import datetime as dt
import struct
import os
import logging
logging.basicConfig(filename='/home/ccaruser/lidar.log', level=logging.INFO)


def save_to_dc(cache, t, data):
    cache[bytes(str(t), 'utf-8')] = data


def send_old(cache, url, key):
    for i in cache:
        if send(url, key, cache[i], 'Old'):
            del cache[i]


def call_send(url, key, data, t, cache):
    """ Function for sending packets. This is called in a separate thread to ensure all data is collected. This function
    runs until it receives a good code from the server. """
    # Send old data
    send_old(cache, url, key)

    # Send current data
    if not send(url, key, data, 'New'):
        save_to_dc(cache, t, data)
        logging.info('No connection made. Data saved to cache. ')


def send(url, key, data, s):
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
    logging.info(s + " LiDAR Packet sent at " + str(dt.datetime.utcnow()))
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
            logging.critical('Negative time:', i, j)
            os._exit(1)
    return header + data
