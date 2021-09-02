#!/usr/bin/python3
# 
# This version reads json from Envoy then publishes the json to mqtt broker
#
# Version 1.0 1st September 2021
#
# Ian Mills
# vk2him@gmail.com
#

import json
import requests
import threading
from requests.auth import HTTPDigestAuth
import pprint

import paho.mqtt.client as mqtt
client = mqtt.Client()

pp = pprint.PrettyPrinter()

#
##### Settings Start here
#
# I use the Home Assistant Mosquitto broker add-on.
#
# As described in the Documentation for the Mosquitto broker add-on,
# the MQTT user/password are the user setup for mqtt.
# If you use an extrenal broker, use those details instead
# 
# Note - if issues connecting, use FQDN for broker IP instead of hassio.local
#
MQTT_HOST = "hassio.local"
MQTT_PORT = "1883"
MQTT_TOPIC = "/envoy/json"  # Note - if you change this topic, you'll need to also change the value_templates in configuration.yaml
MQTT_USER = "secret"
MQTT_PASSWORD = "secret"
#
# envoy-s host IP
#  ** Note - use FQDN and not envoy.local if issues connecting
host = 'envoy.local'
# envoy installer password - generate from seperate python script
password = 'secret'
#
####  End Settings - no changes after this line
#
#


user = 'installer'
auth = HTTPDigestAuth(user, password)
marker = b'data: '

# The callback for when the client receives a CONNACK response from the server.
    # Subscribing after on_connect() means that if the connection is lost
    # the subscription will be renewed when reconnecting.
    #The parameter rc is an integer giving the return code:
    #0: Success
    #1: Refused – unacceptable protocol version
    #2: Refused – identifier rejected
    #3: Refused – server unavailable
    #4: Refused – bad user name or password (MQTT v3.1 broker only)
    #5: Refused – not authorised (MQTT v3.1 broker only

def on_connect(client, userdata, flags, rc):
    """
    Handle connections (or failures) to the broker.
    This is called after the client has received a CONNACK message
    from the broker in response to calling connect().
    The parameter rc is an integer giving the return code:
    0: Success
    1: Refused . unacceptable protocol version
    2: Refused . identifier rejected
    3: Refused . server unavailable
    4: Refused . bad user name or password (MQTT v3.1 broker only)
    5: Refused . not authorised (MQTT v3.1 broker only)
    """
    if rc == 0:
        print("Connected to %s:%s" % (MQTT_HOST, MQTT_PORT))
        # Subscribe to our incoming topic
        client.subscribe(MQTT_TOPIC)
        print("{0}".format(MQTT_TOPIC))

    elif rc == 1:
        print("Connection refused - unacceptable protocol version")
    elif rc == 2:
        print("Connection refused - identifier rejected")
    elif rc == 3:
        print("Connection refused - server unavailable")
    elif rc == 4:
        print("Connection refused - bad user name or password")
    elif rc == 5:
        print("Connection refused - not authorised")
    else:
        print("Connection failed - result code %d" % (rc))

def on_publish(client, userdata, mid) :
    print("mid: {0}".format(str(mid)))

def on_disconnect(client, userdata, rc) :
    print("Disconnect returned:")
    print("client: {0}".format(str(client)))
    print("userdata: {0}".format(str(userdata)))
    print("result: {0}".format(str(rc)))

def on_log(client, userdata, level, buf) :
    print("{0}".format(buf))

client               = mqtt.Client()
client.on_connect    = on_connect
#client.on_publish    = on_publish
client.on_disconnect = on_disconnect
# Uncomment to enable debug messages
#client.on_log       = on_log

client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

client.connect(MQTT_HOST,int(MQTT_PORT), 30)

client.loop_start()

"""
Sample truncated output data:

data: {
    "production": {
        "ph-a": 
        "ph-b": {
        "ph-c": {
            "p": -3.155,
            "q": 241.832,
            "s": 244.717,
            "v": 246.138,
            "i": 0.994,
            "pf": 0.0,
            "f": 50.0
    "total-consumption":{
    "net-consumption": {
"""

def scrape_stream():
    while True:
        try:
            url = 'http://%s/stream/meter' % host
            stream = requests.get(url, auth=auth, stream=True, timeout=5)
            for line in stream.iter_lines():
                if line.startswith(marker):
                    data = json.loads(line.replace(marker, b''))
                    json_string = json.dumps(data)
                    #pp.pprint(json_string)
                                    
                    client.publish(topic= MQTT_TOPIC , payload= json_string, qos=0 )

        except requests.exceptions.RequestException as e:
            print('Exception fetching stream data: %s' % e)

def main():
    stream_thread = threading.Thread(target=scrape_stream)
    #    stream_thread.setDaemon(True)
    stream_thread.start()

if __name__ == '__main__':
    main()