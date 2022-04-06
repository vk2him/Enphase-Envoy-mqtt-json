# Python script: `Enphase Envoy mqtt json for Home Assistant`

A Python script that takes a real time json stream from Enphase Envoy and publishes to a mqtt broker. This can then be used within Home Assistant or for other applications. The data updates at least once per second with negligible load on the Envoy.

**Note - It will not work on 7.x.x firmware as the authentication has changed and the password generator will not work.**

**If you have 7.x.x, you can contact Enphase Support and request they downgrade or keep you permanently on firmware 5.x.x .**

# Requirements

- An Enphase Envoy running 5.x.x firmware.
- A system running python3 with the modules `paho.mqtt` , `requests` and `pprint`
- The serial number of your Envoy which can be obtained by browsing to "http://envoy.local"
- The installer password for your envoy. To obtain, run the `passwordCalc.py` script using the Envoys serial number after first editing `passwordCalc.py` and inserting your serial number. Don't change the `userName` - it must be installer
    - The serial number program is courtesy of "https://github.com/sarnau/EnphaseEnergy"
- A mqtt broker - this can be external or use the `Mosquitto broker` from the Home Assistant Add-on store
    - If you use the HA broker add-on, create a Home Assistant user/password for mqtt as described in the `Mosquitto broker` installation instructions
     

# Installation Method 1 - as a Docker container within Home Assistant. ###

We will be manually installing the script into Home Assistant as a "Local add-on" and these are stored in a shared folder called "addons" (as opposed to "Official add-ons which are available from the Add-on store).

We will be using Samba share add-on from the Official add-ons page, so please install this first if not already. 
  
   https://my.home-assistant.io/redirect/supervisor_addon/?addon=core_samba

__Note:__ - Ensure Samba share is working so files can be copied to your `addons` directory



__HA Installation Step 1__

1) Copy all the files from this repo to a new folder on your local PC. Remember the name of this folder 
   - Alternatively you could do this via `git clone https://github.com/vk2him/Enphase-Envoy-mqtt-json` 
2) Configure settings in `envoy_to_mqtt_json.py`
3) Within Home Assistant, create a directory inside ```addons``` that will store the files from step 1)
    - I use the name "Enphase-Envoy-mqtt-json"
4) Using the Samba share, Copy files from your local PC folder to the Home Assistant ```addons/Enphase-Envoy-mqtt-json``` directory from step 3)
5) Open the Home Assistant frontend
    - Go to "Configuration"
    - Click on "Add-ons, backups & Supervisor"
    - Click "add-on store" in the bottom right corner.

      https://my.home-assistant.io/redirect/supervisor_store/

    - On the top right overflow menu, click the "Check for updates" button
    - You should now see a new section at the top of the store called "Local add-ons" that lists this add-on
      <img src="images/addon.jpg">
    - Click on the add-on to go to the add-on details page.
    - Click to Install the add-on
    - Start the add-on
    - Optionally slide switch to enable Watchdog and/or Auto update
    - Click on the "Logs" tab, and refresh the logs, you should now see output similar to this:

            [s6-init] making user provided files available at /var/run/s6/etc...exited 0.
            [s6-init] ensuring user provided files have correct perms...exited 0.
            [fix-attrs.d] applying ownership & permissions fixes...
            [fix-attrs.d] done.
            [cont-init.d] executing container initialization scripts...
            [cont-init.d] done.
            [services.d] starting services
            [services.d] done.
            06/04/2022 16:52:14  Connected to 192.168.1.74:1883
            /envoy/json
6) mqtt steam will now be sent to your broker

  __If you have problems with the above, follow this guide__

   https://developers.home-assistant.io/docs/add-ons/tutorial/

7) Configure sensors etc to use the mqtt stream

## `configuration.yaml` configuration examples
```yaml
# Example configuration.yaml entry
#
# Creates sensors with names such as sensor.mqtt_production
#
sensor:
  - platform: mqtt
    state_topic: "/envoy/json"
    name: "mqtt_production"
    qos: 0
    unit_of_measurement: "W"
    value_template: '{% if is_state("sun.sun", "below_horizon")%}0{%else%}{{ value_json["production"]["ph-a"]["p"]  | int(0) }}{%endif%}'
    state_class: measurement
    device_class: power

  - platform: mqtt
    state_topic: "/envoy/json"
    value_template: '{{ value_json["total-consumption"]["ph-a"]["p"] }}'
    name: "mqtt_consumption"
    qos: 0
    unit_of_measurement: "W"
    state_class: measurement
    device_class: power

  - platform: mqtt
    state_topic: "/envoy/json"
    name: "mqtt_power_factor"
    qos: 0
    unit_of_measurement: "%"
    value_template: '{{ value_json["total-consumption"]["ph-a"]["pf"] }}'
    state_class: measurement
    device_class: power_factor

  - platform: mqtt
    state_topic: "/envoy/json"
    name: "mqtt_voltage"
    qos: 0
    unit_of_measurement: "V"
    value_template: '{{ value_json["total-consumption"]["ph-a"]["v"] }}'
    state_class: measurement
    device_class: voltage
#
```

## `value_template` configuration examples
```yaml
value_template: '{{ value_json["total-consumption"]["ph-a"]["p"] }}' # Phase A Total power consumed by house
value_template: '{{ value_json["net-consumption"]["ph-c"]["p"] }}'   # Phase C - Total Power imported or exported
value_template: '{{ value_json["production"]["ph-b"]["v"] }}'   # Phase B - Voltage produced by panels
value_template: '{{ value_json["production"]["ph-a"]["p"] | int + value_json["production"]["ph-b"]["p"] | int + value_json["production"]["ph-c"]["p"] | int }}'  # Adding all three Production phases

```

## Real time power display using Power Wheel Card

Here's the code if you'd like real-time visualisations of your power usage like this:

<img src="images/Power-wheel-card.jpeg">

Power Wheel card:

```yaml
active_arrow_color: '#FF0000'
color_icons: true
consuming_color: '#FF0000'
grid_power_consumption_entity: sensor.importing
grid_power_production_entity: sensor.exporting
home_icon: mdi:home-outline
icon_height: mdi:18px
producing_colour: '#00FF00'
solar_icon: mdi:solar-power
solar_power_entity: sensor.solarpower
title_power: ' '
type: custom:power-wheel-card
```
configuration.yaml:

```yaml
sensor:
  
  #
  # These ones are for Envoy via mqtt
  #
  - platform: mqtt
    state_topic: "/envoy/json"
    name: "mqtt_production"
    qos: 0
    unit_of_measurement: "W"
    value_template: '{% if is_state("sun.sun", "below_horizon")%}0{%else%}{{ value_json["production"]["ph-a"]["p"]  | int(0) }}{%endif%}'
    state_class: measurement
    device_class: power

  - platform: mqtt
    state_topic: "/envoy/json"
    value_template: '{{ value_json["total-consumption"]["ph-a"]["p"] }}'
    name: "mqtt_consumption"
    qos: 0
    unit_of_measurement: "W"
    state_class: measurement
    device_class: power

  - platform: template
    sensors:
      exporting:
        friendly_name: "Current MQTT Energy Exporting"
        value_template: "{{ [0, (states('sensor.mqtt_production') | int(0) - states('sensor.mqtt_consumption') | int(0))] | max }}"
        unit_of_measurement: "W"
        icon_template: mdi:flash
      importing:
        friendly_name: "Current MQTT Energy Importing"
        value_template: "{{ [0, (states('sensor.mqtt_consumption') | int(0) - states('sensor.mqtt_production') | int(0))] | max }}"
        unit_of_measurement: "W"
        icon_template: mdi:flash
      solarpower:
        friendly_name: "Solar MQTT Power"
        value_template: "{{ states('sensor.mqtt_production')}}"
        unit_of_measurement: "W"
        icon_template: mdi:flash
```

# Installation Method 2 - as a stand-alone install on a Linux host

- Copy to you Linux host in the directory of your choosing 
`git clone https://github.com/vk2him/Enphase-Envoy-mqtt-json`
- Configure settings in `envoy_to_mqtt_json.py`

__Note:__

  - You need to install `paho.mqtt` :- 
```
    pip install paho-mqtt
```
- If that doesn't work, try
```
git clone https://github.com/eclipse/paho.mqtt.python
cd paho.mqtt.python
python setup.py install
```

## To manually run Script
```
/path/to/python3 /path/to/envoy_to_mqtt_json.py
```

## Run automatically as a systemd service on Linux Mint,Ubuntu, etc

Note: this should work for any linux distribution that uses systemd services, but the instructions and locations may vary slightly.

Take note of where your python file has been saved as you need to point to it in the service file

```
/path/to/envoy_to_mqtt_json.py
```

Using a bash terminal

```
cd /etc/systemd/system
```

Create a file called envoy.service with your favourite file editor and add the following (alter User/Group to suit). 

```

[Unit]
Description=Envoy stream to MQTT
Documentation=https://github.com/vk2him/Enphase-Envoy-mqtt-json
After=network.target mosquitto.service
StartLimitIntervalSec=0

[Service]
Type=simple
User=youruserid
Group=yourgroupid
ExecStart=/path/to/python3 /path/to/envoy_to_mqtt_json.py
Environment=PYTHONUNBUFFERED=true
Restart=always
RestartSec=5
SyslogIdentifier=envoy
StandardError=journal

[Install]
WantedBy=multi-user.target

```

Save and close the file then run the following commands

```
sudo systemctl daemon-reload
```
```
sudo systemctl enable envoy.service
```
```
sudo systemctl start envoy.service
```
You can check the status of the service at any time by the command
```
systemctl status envoy
```

## Run automatically on macOs as a LaunchAgent

 - an example for `macOs` is to create a `~/Library/LaunchAgents/envoy.plist`

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Disabled</key>
	<false/>
	<key>EnvironmentVariables</key>
	<dict>
		<key>PATH</key>
		<string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Library/Apple/usr/bin:/usr/local/sbin</string>
	</dict>
	<key>KeepAlive</key>
	<true/>
	<key>Label</key>
	<string>envoy</string>
	<key>ProgramArguments</key>
	<array>
		<string>/path/to/python3</string>
		<string>/path/to/envoy_to_mqtt_json.py</string>
	</array>
	<key>RunAtLoad</key>
	<true/>
</dict>
</plist>
```
Then use `launchctl` to load the plist from a terminal:
```
launchctl load ~/Library/LaunchAgents/envoy.plist
```

To stop it running use

```
launchctl unload ~/Library/LaunchAgents/envoy.plist
```

# Example output
The resulting mqtt topic should look like this example:
```
{
    "production": {
        "ph-a": {
            "p": 351.13,
            "q": 317.292,
            "s": 487.004,
            "v": 244.566,
            "i": 1.989,
            "pf": 0.72,
            "f": 50.0
        },
        "ph-b": {
            "p": 0.0,
            "q": 0.0,
            "s": 0.0,
            "v": 0.0,
            "i": 0.0,
            "pf": 0.0,
            "f": 0.0
        },
        "ph-c": {
            "p": 0.0,
            "q": 0.0,
            "s": 0.0,
            "v": 0.0,
            "i": 0.0,
            "pf": 0.0,
            "f": 0.0
        }
    },
    "net-consumption": {
        "ph-a": {
            "p": 21.397,
            "q": -778.835,
            "s": 865.208,
            "v": 244.652,
            "i": 3.539,
            "pf": 0.03,
            "f": 50.0
        },
        "ph-b": {
            "p": 0.0,
            "q": 0.0,
            "s": 0.0,
            "v": 0.0,
            "i": 0.0,
            "pf": 0.0,
            "f": 0.0
        },
        "ph-c": {
            "p": 0.0,
            "q": 0.0,
            "s": 0.0,
            "v": 0.0,
            "i": 0.0,
            "pf": 0.0,
            "f": 0.0
        }
    },
    "total-consumption": {
        "ph-a": {
            "p": 372.528,
            "q": -1096.126,
            "s": 1352.165,
            "v": 244.609,
            "i": 5.528,
            "pf": 0.28,
            "f": 50.0
        },
        "ph-b": {
            "p": 0.0,
            "q": 0.0,
            "s": 0.0,
            "v": 0.0,
            "i": 0.0,
            "pf": 0.0,
            "f": 0.0
        },
        "ph-c": {
            "p": 0.0,
            "q": 0.0,
            "s": 0.0,
            "v": 0.0,
            "i": 0.0,
            "pf": 0.0,
            "f": 0.0
        }
    }
}
```

__Note:__ Data is provided for three phases - unused phases have values of `0.0`

## Description of labels 
- more info here "https://www.greenwoodsolutions.com.au/news-posts/real-apparent-reactive-power"

```
"production": = Solar panel production - always positive value
"total-consumption": = Total Power consumed - always positive value
"net-consumption": = Total power Consumed minus Solar panel production. Will be positive when importing and negative when exporting
    
    "ph-a" = Phase A    
    "ph-b" = Phase B
    "ph-c" = Phase C

        "p": =  Real Power ** This is the one to use
        "q": =  Reactive Power
        "s": =  Apparent Power
        "v": =  Voltage
        "i": =  Current
        "pf": = Power Factor
        "f": =  Frequency
```          

## Donation
If this project helps you, you can give me a cup of coffee<br/>
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/vk2him)
<br/><br/>
