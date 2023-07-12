#!/usr/bin/python3
# 
# This version reads json from Envoy then publishes the json to mqtt broker
#
# Version 1.0 1st September 2021 - Initial release
# Version 1.1 7th November 2021 - Include date/time to output for checking 
# Version 1.2 6th April 2022 - tidy up some comments
# Version 1.3 7th April 2022 - converted to work as a Home Assistant Addon
#
# Ian Mills
# vk2him@gmail.com
#

import json
import urllib3
import requests
import threading
#from requests.auth import HTTPDigestAuth
import pprint
from datetime import datetime
import time

#disable warnings of self signed certificate https
urllib3.disable_warnings()

import paho.mqtt.client as mqtt
client = mqtt.Client()

pp = pprint.PrettyPrinter()

import json

with open("/data/options.json", "r") as f:
    option_dict = json.load(f)
# print(option_dict["x"])

##

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
#print ("date =", dt_string)

#
##### Settings Start here
#
# I use the Home Assistant Mosquito broker add-on but you can use an external one if needed
# python
global ENVOY_TOKEN
ENVOY_TOKEN = None
MQTT_HOST = option_dict["MQTT_HOST"]  # Note - if issues connecting, use FQDN for broker IP instead of hassio.local
MQTT_PORT = option_dict["MQTT_PORT"]
MQTT_TOPIC = "envoy/json"  # Note - if you change this topic, you'll need to also change the value_templates in configuration.yaml
MQTT_USER = option_dict["MQTT_USER"]     # As described in the Documentation for the HA Mosquito broker add-on, the MQTT user/password are the user setup for mqtt
MQTT_PASSWORD = option_dict["MQTT_PASSWORD"]    # If you use an external broker, use those details instead
MQTT_TOPIC_FREEDS = option_dict["TOPIC_FREEDS"]
ENVOY_HOST = option_dict["ENVOY_HOST"]  # ** Enter envoy-s IP. Note - use FQDN and not envoy.local if issues connecting 
ENVOY_USER = option_dict["ENVOY_USER"] 
ENVOY_USER_PASS = option_dict["ENVOY_USER_PASS"]
ENVOY_PASSWORD = option_dict["ENVOY_PASSWORD"]   # This is the envoy's installer password - generate the password from the separate python script
ENVOY_TOKEN = option_dict["ENVOY_TOKEN"]  # manualy generate token at https://entrez.enphaseenergy.com/entrez_tokens

####  End Settings - no changes after this line

#Token generator
url_info ='https://%s/info' % ENVOY_HOST
def token_gen(token):
    if token is None or token=='':
        print(dt_string,'No token avaliable, generating one')
        envoy_serial = requests.get(url_info, verify=False)
        if envoy_serial.status_code != 200:
            print(dt_string,'Failed connect to Envoy to get serial number got ', envoy_serial, 'Verify URL', url_info )
        else:
            envoy_serial=envoy_serial.text.partition('</sn>')[0].partition('<sn>')[2]
            data = {'user[email]': ENVOY_USER, 'user[password]': ENVOY_USER_PASS}
            response = requests.post('https://enlighten.enphaseenergy.com/login/login.json?', data=data)
            if response.status_code != 200:
                print(dt_string,'Failed connect to https://enlighten.enphaseenergy.com/login/login.json? to generate token part 1 got', response, ' using this info', data )
            else:
                response_data = json.loads(response.text)
                data = {'session_id': response_data['session_id'], 'serial_num': envoy_serial, 'username': ENVOY_USER}
                response = requests.post('https://entrez.enphaseenergy.com/tokens', json=data)
                if response.status_code != 200:
                    print(dt_string,'Failed connect to https://entrez.enphaseenergy.com/tokens to generate token part 2 got', response, ' using this info', data )
                else:
                    print(dt_string,'Token generated', response.text)
                    return response.text
    else:
        return token

ENVOY_TOKEN=token_gen(ENVOY_TOKEN)
#user = 'installer'
#auth = HTTPDigestAuth(user, ENVOY_PASSWORD)
#marker = b''
activate_json={"enable": 1}

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
        print(dt_string," Connected to %s:%s" % (MQTT_HOST, MQTT_PORT))
        # Subscribe to our incoming topic
        client.subscribe(MQTT_TOPIC)
        print("{0}".format(MQTT_TOPIC))

    elif rc == 1:
        print(dt_string," Connection refused - unacceptable protocol version")
    elif rc == 2:
        print(dt_string," Connection refused - identifier rejected")
    elif rc == 3:
        print(dt_string," Connection refused - server unavailable")
    elif rc == 4:
        print(dt_string," Connection refused - bad user name or password")
    elif rc == 5:
        print(dt_string," Connection refused - not authorised")
    else:
        print(dt_string," Connection failed - result code %d" % (rc))

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

# Add 10 second sleep to allow initialise

time.sleep(10)

print(dt_string," Connected to %s:%s" % (MQTT_HOST, MQTT_PORT))

client.loop_start()

def scrape_stream_production():
    while True:
        try:
            url = 'http://%s/production.json' % ENVOY_HOST
            headers = {"Authorization": "Bearer " + ENVOY_TOKEN}
            stream = requests.get(url, timeout=5, verify=False, headers=headers)
            if stream.status_code == 401:
                print(dt_string,'Failed to autenticate', stream, ' generating new token')
                ENVOY_TOKEN=token_gen(None)
                headers = {"Authorization": "Bearer " + ENVOY_TOKEN}
                stream = requests.get(url, timeout=5, verify=False, headers=headers)
            if stream.status_code != 200:
                print(dt_string,'Failed connect to Envoy got ', stream)
            else:
                for line in stream.iter_lines():
                    if line.startswith(line):
                        #data = json.loads(line.replace(marker, b''))
                        data = json.loads(line)
                        json_string = json.dumps(data)
                        #pp.pprint(json_string)
                        json_string_freeds = data['consumption'][0]['wNow']
                        #pp.pprint(json_string_freeds)
                        client.publish(topic= MQTT_TOPIC , payload= json_string, qos=0 )
                        client.publish(topic= MQTT_TOPIC_FREEDS , payload= json_string_freeds, qos=0 )
        except requests.exceptions.RequestException as e:
            print(dt_string, ' Exception fetching stream data: %s' % e)

def scrape_stream_livedata():
    global ENVOY_TOKEN
    while True:
        try:
            url = 'https://%s/ivp/livedata/status' % ENVOY_HOST 
            headers = {"Authorization": "Bearer " + ENVOY_TOKEN}
            stream = requests.get(url, timeout=5, verify=False, headers=headers)
            if stream.status_code == 401:
                print(dt_string,'Failed to autenticate', stream, ' generating new token')
                ENVOY_TOKEN=token_gen(None)
                headers = {"Authorization": "Bearer " + ENVOY_TOKEN}
                stream = requests.get(url, timeout=5, verify=False, headers=headers)
            if stream.status_code != 200:
                print(dt_string,'Failed connect to Envoy got ', stream)
            elif stream.json()['connection']['sc_stream'] == 'disabled':
                url_activate='https://%s/ivp/livedata/stream' % ENVOY_HOST
                print(dt_string, 'Stream is not active, trying to enable')
                response_activate=requests.post(url_activate, verify=False, headers=headers, json=activate_json)
                if response_activate.json()['sc_stream']=='enabled':
                    stream = requests.get(url, stream=True, timeout=5, verify=False, headers=headers)
                    print(dt_string, 'Success, stream is active now')
                else:
                    print(dt_string, 'Failed to activate stream ', response_activate.content)
            else:
                json_string = json.dumps(stream.json())
                #print(dt_string, 'Json Response:', json_string)
                json_string_freeds = json.dumps(round(stream.json()["meters"]["grid"]["agg_p_mw"]*0.001))
                client.publish(topic= MQTT_TOPIC , payload= json_string, qos=0 )
                client.publish(topic= MQTT_TOPIC_FREEDS , payload= json_string_freeds, qos=0 )
                time.sleep(0.6)
        except requests.exceptions.RequestException as e:
            print(dt_string, ' Exception fetching stream data: %s' % e)

def scrape_stream_meters():
    global ENVOY_TOKEN
    while True:
        try:
            url = 'https://%s/ivp/meters/readings' % ENVOY_HOST 
            headers = {"Authorization": "Bearer " + ENVOY_TOKEN}
            stream = requests.get(url, timeout=5, verify=False, headers=headers)
            if stream.status_code == 401:
                print(dt_string,'Failed to autenticate', stream, ' generating new token')
                ENVOY_TOKEN=token_gen(None)
                headers = {"Authorization": "Bearer " + ENVOY_TOKEN}
                stream = requests.get(url, timeout=5, verify=False, headers=headers)
            if stream.status_code != 200:
                print(dt_string,'Failed connect to Envoy got ', stream)
            else:
                json_string = json.dumps(stream.json())
                #print(dt_string, 'Json Response:', json_string)
                json_string_freeds = json.dumps(round(stream.json()[1]["activePower"]))
                client.publish(topic= MQTT_TOPIC , payload= json_string, qos=0 )
                client.publish(topic= MQTT_TOPIC_FREEDS , payload= json_string_freeds, qos=0 )
                time.sleep(0.6)
        except requests.exceptions.RequestException as e:
            print(dt_string, ' Exception fetching stream data: %s' % e)

def main():
    #Use url https://envoy.local/production.json
    #stream_thread = threading.Thread(target=scrape_stream_production)
    #Use url https://envoy.local/ivp/livedata/status
    #stream_thread = threading.Thread(target=scrape_stream_livedata)
    #Use url https://envoy.local/ivp/meters/reading
    stream_thread = threading.Thread(target=scrape_stream_meters)
    #    stream_thread.setDaemon(True)
    stream_thread.start()

if __name__ == '__main__':
    main()
