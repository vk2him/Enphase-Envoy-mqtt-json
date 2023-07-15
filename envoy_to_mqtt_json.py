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
from requests.auth import HTTPDigestAuth
import threading
import pprint
from datetime import datetime
import time
import xml.etree.ElementTree as ET
#disable warnings of self signed certificate https
urllib3.disable_warnings()
import paho.mqtt.client as mqtt
client = mqtt.Client()
pp = pprint.PrettyPrinter()
import xml.etree.ElementTree as ET
import hashlib


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
ENVOY_TOKEN = None
ENVOY_PASSWORD = None
MQTT_HOST = option_dict["MQTT_HOST"]  # Note - if issues connecting, use FQDN for broker IP instead of hassio.local
MQTT_PORT = option_dict["MQTT_PORT"]
MQTT_TOPIC = option_dict["MQTT_TOPIC"]  # Note - if you change this topic, you'll need to also change the value_templates in configuration.yaml
MQTT_USER = option_dict["MQTT_USER"]     # As described in the Documentation for the HA Mosquito broker add-on, the MQTT user/password are the user setup for mqtt
MQTT_PASSWORD = option_dict["MQTT_PASSWORD"]    # If you use an external broker, use those details instead
MQTT_TOPIC_FREEDS = option_dict["TOPIC_FREEDS"]
ENVOY_HOST = option_dict["ENVOY_HOST"]  # ** Enter envoy-s IP. Note - use FQDN and not envoy.local if issues connecting 
ENVOY_USER= option_dict["ENVOY_USER"]
ENVOY_USER_PASS= option_dict["ENVOY_USER_PASS"]

#Password generator
userName = b'installer'
DEFAULT_REALM = b'enphaseenergy.com'
gSerialNumber = None

####  End Settings - no changes after this line


# Get info
url_info ='http://%s/info' % ENVOY_HOST
response_info = requests.get(url_info, verify=False)
if response_info.status_code != 200:
    print(dt_string,'Failed connect to Envoy to get info got ', response_info, 'Verify URL', url_info )
else:
    root = ET.fromstring(response_info.content)
    serialNumber = [child.text for child in root.iter('sn')]
    version = [child.text for child in root.iter('software')]

if len(serialNumber) != 0:
    serialNumber = serialNumber[0]
    print(dt_string,'Serial number:', serialNumber)
else:
    print (dt_string,'Cannot decode serial number did not got valid XML for <sn> from ', url)
    print (dt_string,'Response content:', response.content)

if len(version) != 0:
    if version[0].count('D7.') == 1:
        print (dt_string,'Detected FW version 7')
        envoy_version=7
    elif version[0].count('D5.') == 1:
        print (dt_string,'Detected FW version 5')
        envoy_version=5
    else:
        print (dt_string,'Cannot match firmware version, got ', version)
else:
    print (dt_string,'Cannot decode firmware version, did not got valid XML for <software> from ', url)
    print (dt_string,'Response content:', response.content)

#Token generator
def token_gen(token):
    if token is None or token=='':
        print(dt_string,'No token avaliable, generating one')
        # envoy_serial = requests.get(url_info, verify=False)
        # if envoy_serial.status_code != 200:
        #     print(dt_string,'Failed connect to Envoy to get serial number got ', envoy_serial, 'Verify URL', url_info )
        # else:
        #     envoy_serial=envoy_serial.text.partition('</sn>')[0].partition('<sn>')[2]
        data = {'user[email]': ENVOY_USER, 'user[password]': ENVOY_USER_PASS}
        response = requests.post('https://enlighten.enphaseenergy.com/login/login.json?', data=data)
        if response.status_code != 200:
            print(dt_string,'Failed connect to https://enlighten.enphaseenergy.com/login/login.json? to generate token part 1 got', response, ' using this info', data )
        else:
            response_data = json.loads(response.text)
            data = {'session_id': response_data['session_id'], 'serial_num': serialNumber, 'username': ENVOY_USER}
            response = requests.post('https://entrez.enphaseenergy.com/tokens', json=data)
            if response.status_code != 200:
                print(dt_string,'Failed connect to https://entrez.enphaseenergy.com/tokens to generate token part 2 got', response, ' using this info', data )
            else:
                print(dt_string,'Token generated', response.text)
                return response.text
    else:
        return token

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
#print(dt_string," Connected to %s:%s" % (MQTT_HOST, MQTT_PORT))

client.loop_start()

## Generation of Envoy password based on serial number, copy from https://github.com/sarnau/EnphaseEnergy/passwordCalc.py
## Credits to Markus Fritze https://github.com/sarnau/EnphaseEnergy
def emupwGetPasswdForSn(serialNumber, userName, realm):
    if serialNumber == None or userName == None:
        return None
    if realm == None:
        realm = DEFAULT_REALM
    return hashlib.md5(b'[e]' + userName + b'@' + realm + b'#' + serialNumber + b' EnPhAsE eNeRgY ').hexdigest()

def emupwGetPasswd(userName,realm):
    global gSerialNumber
    if gSerialNumber:
        return emupwGetPasswdForSn(gSerialNumber, userName, realm);
    return None;

def emupwGetPublicPasswd(serialNumber, userName, realm, expiryTimestamp=0):
    if expiryTimestamp==0:
        expiryTimestamp = int(time.time());
    return hashlib.md5(userName + b'@' + realm + b'#' + serialNumber + b'%d' % expiryTimestamp).hexdigest()

def emupwGetMobilePasswd(serialNumber,userName,realm=None):
    global gSerialNumber
    gSerialNumber = serialNumber
    digest = emupwGetPasswdForSn(serialNumber,userName,realm)
    countZero = digest.count('0')
    countOne = digest.count('1')
    password = ''
    for cc in digest[::-1][:8]:
        if countZero == 3 or countZero == 6 or countZero == 9:
            countZero = countZero -1
        if countZero > 20:
            countZero = 20
        if countZero < 0:
            countZero = 0

        if countOne == 9 or countOne == 15:
            countOne = countOne -1
        if countOne > 26:
            countOne = 26
        if countOne < 0:
            countOne = 0
        if cc == '0':
            password += chr(ord('f') + countZero)
            countZero = countZero - 1
        elif cc == '1':
            password += chr(ord('@') + countOne)
            countOne = countOne -1
        else:
            password += cc
    return password


def scrape_stream_production():
    global ENVOY_TOKEN
    ENVOY_TOKEN=token_gen(ENVOY_TOKEN)
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
            elif stream.status_code != 200:
                print(dt_string,'Failed connect to Envoy got ', stream)
            else:
                for line in stream.iter_lines():
                    if line.startswith(line):
                        data = json.loads(line)
                        json_string = json.dumps(data)
                        #pp.pprint(json_string)
                        json_string_freeds = data['consumption'][0]['wNow']
                        #pp.pprint(json_string_freeds)
                        client.publish(topic= MQTT_TOPIC , payload= json_string, qos=0 )
                        if len(MQTT_TOPIC_FREEDS) >=1: client.publish(topic= MQTT_TOPIC_FREEDS , payload= json_string_freeds, qos=0 )
        except requests.exceptions.RequestException as e:
            print(dt_string, ' Exception fetching stream data: %s' % e)

def scrape_stream_livedata():
    global ENVOY_TOKEN
    ENVOY_TOKEN=token_gen(ENVOY_TOKEN)
    activate_json={"enable": 1}
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
            elif stream.status_code != 200:
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
                if len(MQTT_TOPIC_FREEDS) >=1: client.publish(topic= MQTT_TOPIC_FREEDS , payload= json_string_freeds, qos=0 )
                time.sleep(0.6)
        except requests.exceptions.RequestException as e:
            print(dt_string, ' Exception fetching stream data: %s' % e)

def scrape_stream_meters():
    global ENVOY_TOKEN
    ENVOY_TOKEN=token_gen(ENVOY_TOKEN)
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
            elif stream.status_code != 200:
                print(dt_string,'Failed connect to Envoy got ', stream)
            else:
                json_string = json.dumps(stream.json())
                #print(dt_string, 'Json Response:', json_string)
                json_string_freeds = json.dumps(round(stream.json()[1]["activePower"]))
                client.publish(topic= MQTT_TOPIC , payload= json_string, qos=0 )
                if len(MQTT_TOPIC_FREEDS) >=1: client.publish(topic= MQTT_TOPIC_FREEDS , payload= json_string_freeds, qos=0 )
                time.sleep(0.6)
        except requests.exceptions.RequestException as e:
            print(dt_string, ' Exception fetching stream data: %s' % e)
# Example JSON output:
"""
[
    {
        "eid": 704643328,
        "timestamp": 1689409016,
        "actEnergyDlvd": 0.063,
        "actEnergyRcvd": 7939.998,
        "apparentEnergy": 63680.783,
        "reactEnergyLagg": 788.493,
        "reactEnergyLead": 3.712,
        "instantaneousDemand": 0.000,
        "activePower": 0.000,
        "apparentPower": 43.086,
        "reactivePower": -0.000,
        "pwrFactor": 0.000,
        "voltage": 237.151,
        "current": 0.254,
        "freq": 50.000,
        "channels": [
            {
                "eid": 1778385169,
                "timestamp": 1689409016,
                "actEnergyDlvd": 0.063,
                "actEnergyRcvd": 7939.998,
                "apparentEnergy": 63680.783,
                "reactEnergyLagg": 788.493,
                "reactEnergyLead": 3.712,
                "instantaneousDemand": 0.000,
                "activePower": 0.000,
                "apparentPower": 43.086,
                "reactivePower": -0.000,
                "pwrFactor": 0.000,
                "voltage": 237.151,
                "current": 0.254,
                "freq": 50.000
            },
            {
                "eid": 1778385170,
                "timestamp": 1689409016,
                "actEnergyDlvd": 0.061,
                "actEnergyRcvd": 10104.018,
                "apparentEnergy": 31694.583,
                "reactEnergyLagg": 763.996,
                "reactEnergyLead": 7.749,
                "instantaneousDemand": -0.097,
                "activePower": -0.097,
                "apparentPower": 2.779,
                "reactivePower": 0.000,
                "pwrFactor": 0.000,
                "voltage": 9.994,
                "current": 0.278,
                "freq": 50.000
            },
            {
                "eid": 1778385171,
                "timestamp": 1689409016,
                "actEnergyDlvd": 0.000,
                "actEnergyRcvd": 20943.151,
                "apparentEnergy": 22986.373,
                "reactEnergyLagg": 762.634,
                "reactEnergyLead": 0.866,
                "instantaneousDemand": -0.431,
                "activePower": -0.431,
                "apparentPower": 2.006,
                "reactivePower": -0.000,
                "pwrFactor": -1.000,
                "voltage": 10.346,
                "current": 0.194,
                "freq": 50.000
            }
        ]
    },
    {
        "eid": 704643584,
        "timestamp": 1689409016,
        "actEnergyDlvd": 3917484.219,
        "actEnergyRcvd": 637541.835,
        "apparentEnergy": 8370194.604,
        "reactEnergyLagg": 113560.641,
        "reactEnergyLead": 2299086.122,
        "instantaneousDemand": -161.626,
        "activePower": -161.626,
        "apparentPower": 372.559,
        "reactivePower": -212.953,
        "pwrFactor": -0.431,
        "voltage": 237.273,
        "current": 1.571,
        "freq": 50.000,
        "channels": [
            {
                "eid": 1778385425,
                "timestamp": 1689409016,
                "actEnergyDlvd": 3917484.219,
                "actEnergyRcvd": 637541.835,
                "apparentEnergy": 8370194.604,
                "reactEnergyLagg": 113560.641,
                "reactEnergyLead": 2299086.122,
                "instantaneousDemand": -161.626,
                "activePower": -161.626,
                "apparentPower": 372.559,
                "reactivePower": -212.953,
                "pwrFactor": -0.431,
                "voltage": 237.273,
                "current": 1.571,
                "freq": 50.000
            },
            {
                "eid": 1778385426,
                "timestamp": 1689409016,
                "actEnergyDlvd": 0.000,
                "actEnergyRcvd": 18677.254,
                "apparentEnergy": 10322.864,
                "reactEnergyLagg": 798.595,
                "reactEnergyLead": 0.000,
                "instantaneousDemand": -0.222,
                "activePower": -0.222,
                "apparentPower": 0.898,
                "reactivePower": 0.000,
                "pwrFactor": 0.000,
                "voltage": 3.024,
                "current": 0.297,
                "freq": 50.000
            },
            {
                "eid": 1778385427,
                "timestamp": 1689409016,
                "actEnergyDlvd": 0.064,
                "actEnergyRcvd": 27672.079,
                "apparentEnergy": 115.734,
                "reactEnergyLagg": 799.004,
                "reactEnergyLead": 7.648,
                "instantaneousDemand": -0.000,
                "activePower": -0.000,
                "apparentPower": 0.000,
                "reactivePower": 0.000,
                "pwrFactor": 0.000,
                "voltage": 7.651,
                "current": 0.000,
                "freq": 50.000
            }
        ]
    }
]'
"""

def scrape_stream():
    global ENVOY_PASSWORD
    serial = serialNumber.encode("utf-8")
    if ENVOY_PASSWORD =='' or ENVOY_PASSWORD == None : ENVOY_PASSWORD=emupwGetMobilePasswd(serial, userName)
    print(dt_string, 'Envoy password is', ENVOY_PASSWORD)
    auth = HTTPDigestAuth(userName.decode(), ENVOY_PASSWORD)
    marker = b'data: '
    while True:
        try:
            url = 'http://%s/stream/meter' % ENVOY_HOST
            stream = requests.get(url, auth=auth, stream=True, verify=False, timeout=5)
            if stream.status_code == 401:
                print(dt_string,'Failed to autenticate', stream)
            elif stream.status_code != 200:
                print(dt_string,'Failed connect to Envoy got ', stream)
            else:
                for line in stream.iter_lines():
                    if line.startswith(marker):
                        data = json.loads(line.replace(marker, b''))
                        json_string = json.dumps(data)
                        #print(dt_string, 'Json Response:', json_string)
                        json_string_freeds = data['net-consumption']['ph-a']['p']                
                        client.publish(topic= MQTT_TOPIC , payload= json_string, qos=0 )
                        if len(MQTT_TOPIC_FREEDS) >=1: client.publish(topic= MQTT_TOPIC_FREEDS , payload= json_string_freeds, qos=0 )
        except requests.exceptions.RequestException as e:
            print(dt_string, ' Exception fetching stream data: %s' % e)
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

def main():
    #Use url https://envoy.local/production.json
    #stream_thread = threading.Thread(target=scrape_stream_production)
    #Use url https://envoy.local/ivp/livedata/status
    #stream_thread = threading.Thread(target=scrape_stream_livedata)   
    #Use url https://envoy.local/ivp/meters/reading
    #stream_thread = threading.Thread(target=scrape_stream_meters)
    
    if envoy_version == 7:
        stream_thread = threading.Thread(target=scrape_stream_meters)
    elif envoy_version == 5:
        stream_thread = threading.Thread(target=scrape_stream)
    else:
        print(dt_string,'Don''t know what version to use')
    stream_thread.start()

if __name__ == '__main__':
    main()
