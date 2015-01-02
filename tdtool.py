#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import getopt
import httplib
import urllib
import json
import os
import oauth.oauth as oauth
from configobj import ConfigObj

PUBLIC_KEY = ''
PRIVATE_KEY = ''

TELLSTICK_TURNON = 1
TELLSTICK_TURNOFF = 2
TELLSTICK_BELL = 4
TELLSTICK_DIM = 16
TELLSTICK_UP = 128
TELLSTICK_DOWN = 256

TELLSTICK_TEMPERATURE = 1
TELLSTICK_HUMIDITY = 2
TELLSTICK_RAINRATE = 4
TELLSTICK_RAINTOTAL = 8
TELLSTICK_WINDDIRECTION = 16
TELLSTICK_WINDAVERAGE = 32
TELLSTICK_WINDGUST = 64

SUPPORTED_METHODS = TELLSTICK_TURNON | TELLSTICK_TURNOFF | TELLSTICK_BELL | TELLSTICK_DIM | TELLSTICK_UP | TELLSTICK_DOWN
SUPPORTED_SENSOR_METHODS = TELLSTICK_TEMPERATURE | TELLSTICK_HUMIDITY


def print_usage():
    print("Usage: %s [ options ]" % sys.argv[0])
    print("")
    print("Options:")
    print("         -[lsnfdbvh] [ --list ] [ --help ]")
    print("                      [ --sensor sensor ]")
    print("                      [ --on device ] [ --off device ] [ --bell device ]")
    print("                      [ --dimlevel level --dim device ]")
    print("                      [ --up device --down device ]")
    print("")
    print("       --list (-l short option)")
    print("             List currently configured devices and sensors.")
    print("")
    print("       --sensor sensor (-s short option)")
    print("             Display information from the specified sensor.")
    print("")
    print("       --on device (-n short option)")
    print("             Turns on device. 'device' must be an integer of the device-id")
    print("             Device-id and name is outputed with the --list option")
    print("")
    print("       --off device (-f short option)")
    print("             Turns off device. 'device' must be an integer of the device-id")
    print("             Device-id and name is outputed with the --list option")
    print("")
    print("       --dim device (-d short option)")
    print("             Dims device. 'device' must be an integer of the device-id")
    print("             Device-id and name is outputed with the --list option")
    print("             Note: The dimlevel parameter must be set before using this option.")
    print("")
    print("       --dimlevel level (-v short option)")
    print("             Set dim level. 'level' should an integer, 0-255.")
    print("             Note: This parameter must be set before using dim.")
    print("")
    print("       --bell device (-b short option)")
    print("             Sends bell command to devices supporting this. 'device' must")
    print("             be an integer of the device-id")
    print("             Device-id and name is outputed with the --list option")
    print("")
    print("       --up device")
    print("             Sends up command to devices supporting this. 'device' must")
    print("             be an integer of the device-id")
    print("             Device-id and name is outputed with the --list option")
    print("")
    print("       --down device")
    print("             Sends down command to devices supporting this. 'device' must")
    print("             be an integer of the device-id")
    print("             Device-id and name is outputed with the --list option")
    print("")
    print("       --help (-h short option)")
    print("             Shows this screen.")
    print("")
    print("Report bugs to <klippo@deny.se>")


def list_devices():
    devices = do_request('devices/list', {'supportedMethods': SUPPORTED_METHODS})
    sensors = do_request('sensors/list', {'supportedMethods': SUPPORTED_SENSOR_METHODS})
    print("Number of devices: %i" % len(devices['device']))
    for device in devices['device']:
        if device['state'] == TELLSTICK_TURNON:
            state = 'ON'
        elif device['state'] == TELLSTICK_TURNOFF:
            state = 'OFF'
        elif device['state'] == TELLSTICK_DIM:
            state = "DIMMED"
        elif device['state'] == TELLSTICK_UP:
            state = "UP"
        elif device['state'] == TELLSTICK_DOWN:
            state = "DOWN"
        else:
            state = 'Unknown state'

        print("%s\t%s\t%s" % (device['id'], device['name'].ljust(30), state))

    print("\nNumber of sensors: %i" % len(sensors['sensor']))
    for sensor in sensors['sensor']:
        display_sensor(sensor['id'])


def display_sensor(sensor_id):
    sensor_response = do_request('sensor/info', {'id': sensor_id})

    if 'error' in sensor_response:
        print(sensor_response)
        sys.exit(1)
    else:
        name = sensor_response['name']

    print("%s %s" % (sensor_response['id'], name))
    for data in sensor_response['data']:
        unit = ''
        if data['name'] == 'temp':
            unit = u'\N{DEGREE SIGN}'
        elif data['name'] == 'humidity':
            unit = "%"

        print("\t%s\t%s%s" % (data['name'].title().ljust(30), data['value'], unit))


def do_method(device_id, method_id, method_value=0):
    response = do_request('device/info', {'id': device_id})

    if method_id == TELLSTICK_TURNON:
        method = 'on'
    elif method_id == TELLSTICK_TURNOFF:
        method = 'off'
    elif method_id == TELLSTICK_BELL:
        method = 'bell'
    elif method_id == TELLSTICK_UP:
        method = 'up'
    elif method_id == TELLSTICK_DOWN:
        method = 'down'

    if 'error' in response:
        name = ''
        retstring = response['error']
    else:
        name = response['name']
        response = do_request('device/command', {'id': device_id, 'method': method_id, 'value': method_value})
        if 'error' in response:
            retstring = response['error']
        else:
            retstring = response['status']

    if method_id in (TELLSTICK_TURNON, TELLSTICK_TURNOFF):
        print("Turning %s device %s, %s - %s" % (method, device_id, name, retstring))
    elif method_id in (TELLSTICK_BELL, TELLSTICK_UP, TELLSTICK_DOWN):
        print("Sending %s to: %s %s - %s" % (method, device_id, name, retstring))
    elif method_id == TELLSTICK_DIM:
        print("Dimming device: %s %s to %s - %s" % (device_id, name, method_value, retstring))


def do_request(method, params):
    global config
    consumer = oauth.OAuthConsumer(PUBLIC_KEY, PRIVATE_KEY)
    token = oauth.OAuthToken(config['token'], config['tokenSecret'])

    oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token, http_method='GET',
                                                               http_url="http://api.telldus.com/json/" + method,
                                                               parameters=params)
    oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, token)
    headers = oauth_request.to_header()
    headers['Content-Type'] = 'application/x-www-form-urlencoded'

    conn = httplib.HTTPConnection("api.telldus.com:80")
    conn.request('GET', "/json/" + method + "?" + urllib.urlencode(params, True).replace('+', '%20'), headers=headers)

    response = conn.getresponse()
    return json.load(response)


def request_token():
    global config
    consumer = oauth.OAuthConsumer(PUBLIC_KEY, PRIVATE_KEY)
    request = oauth.OAuthRequest.from_consumer_and_token(consumer, http_url='http://api.telldus.com/oauth/requestToken')
    request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, None)
    conn = httplib.HTTPConnection('api.telldus.com:80')
    conn.request(request.http_method, '/oauth/requestToken', headers=request.to_header())

    resp = conn.getresponse().read()
    token = oauth.OAuthToken.from_string(resp)
    print 'Open the following url in your webbrowser:\nhttp://api.telldus.com/oauth/authorize?oauth_token=%s\n' % token.key
    print 'After logging in and accepting to use this application run:\n%s --authenticate' % (sys.argv[0])
    config['requestToken'] = str(token.key)
    config['requestTokenSecret'] = str(token.secret)
    save_config()


def get_access_token():
    global config
    consumer = oauth.OAuthConsumer(PUBLIC_KEY, PRIVATE_KEY)
    token = oauth.OAuthToken(config['requestToken'], config['requestTokenSecret'])
    request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token, http_method='GET',
                                                         http_url='http://api.telldus.com/oauth/accessToken')
    request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, token)
    conn = httplib.HTTPConnection('api.telldus.com:80')
    conn.request(request.http_method, request.to_url(), headers=request.to_header())

    resp = conn.getresponse()
    if resp.status != 200:
        print 'Error retreiving access token, the server replied:\n%s' % resp.read()
        return
    token = oauth.OAuthToken.from_string(resp.read())
    config['requestToken'] = None
    config['requestTokenSecret'] = None
    config['token'] = str(token.key)
    config['tokenSecret'] = str(token.secret)
    print 'Authentication successful, you can now use tdtool'
    save_config()


def authenticate():
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', ['authenticate'])
        for opt, arg in opts:
            if opt in '--authenticate':
                get_access_token()
                return
    except getopt.GetoptError:
        pass
    request_token()


def save_config():
    global config
    try:
        os.makedirs(os.environ['HOME'] + '/.config/Telldus')
    except:
        pass
    config.write()


def main(argv):
    global config
    if 'token' not in config or config['token'] == '':
        authenticate()
        return
    try:
        opts, args = getopt.getopt(argv, "ln:f:d:b:v:h:s:",
                                   ["list", "on=", "off=", "dim=", "bell=", "dimlevel=", "up=", "down=", "help", "sensor"])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    dimlevel = -1

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage()

        elif opt in ("-l", "--list"):
            list_devices()

        elif opt in ("-s", "--sensor"):
            display_sensor(arg)

        elif opt in ("-n", "--on"):
            do_method(arg, TELLSTICK_TURNON)

        elif opt in ("-f", "--off"):
            do_method(arg, TELLSTICK_TURNOFF)

        elif opt in ("-b", "--bell"):
            do_method(arg, TELLSTICK_BELL)

        elif opt in ("-d", "--dim"):
            if dimlevel < 0:
                print("Dimlevel must be set with --dimlevel before --dim")
            else:
                do_method(arg, TELLSTICK_DIM, dimlevel)

        elif opt in ("-v", "--dimlevel"):
            dimlevel = arg

        elif opt in "--up":
            do_method(arg, TELLSTICK_UP)

        elif opt in "--down":
            do_method(arg, TELLSTICK_DOWN)


if __name__ == "__main__":
    config = ConfigObj(os.environ['HOME'] + '/.config/Telldus/tdtool.conf')
    main(sys.argv[1:])
