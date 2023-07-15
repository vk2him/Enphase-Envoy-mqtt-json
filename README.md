# Python script: `Enphase Envoy mqtt json for Home Assistant`

A Python script that takes a real time json stream from Enphase Envoy and publishes to a mqtt broker. This can then be used within Home Assistant or for other applications. The data updates at least once per second with negligible load on the Envoy.

**Note - It will not work on 7.x.x firmware as the authentication method has changed.**

**If you have 7.x.x, you can contact Enphase Support and request they downgrade or keep your Envoy permanently on firmware 5.x.x .**

# Requirements

- An Enphase Envoy running 5.x.x firmware.
- The serial number of your Envoy which can be obtained by browsing to "http://envoy.local"
- The installer password for your envoy. 
  - To obtain the passsword via one of these methods:
    1) Use this online generator: https://blahnana.com/passwordcalc.html
    2) Run the included `passwordCalc.py` python script using your Envoys serial number after first editing `passwordCalc.py` and inserting your serial number. Don't change the `userName` - it must be installer
        - The serial number program is courtesy of "https://github.com/sarnau/EnphaseEnergy"
- A mqtt broker that is already running - this can be external or use the `Mosquitto broker` from the Home Assistant Add-on store
    - If you use the HA broker add-on, create a Home Assistant user/password for mqtt as described in the `Mosquitto broker` installation instructions

# Installation Method 1 - as a Home Assistant addon. ###

1) Add this Repository to your Home Assistant by clicking this button  

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/helderfmf/Enphase-Envoy-mqtt-json)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg

2) After adding the Repository, you'll see a new section titled "vk2him's Enphase add-on repository"
3) Click to install "Stream mqtt from Enphase Envoy"
4) After it's installed, click on "Configuration" and enter required settings __Note:__ "MQTT_HOST" will be the IP address for your mqtt broker, so this will probably be the IP address of your Home Assistant
5) Optionally slide switch to enable Watchdog and/or Auto update
6) Click on the "Logs" tab, you should now see output similar to this:

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
7) mqtt steam will now be sent to your broker

## `configuration.yaml` configuration examples For FW 5
```yaml
# Example configuration.yaml entry
#
# Creates sensors with names such as sensor.mqtt_production
#
sensor:
  - platform: mqtt
    state_topic: "envoy/json"
    name: "mqtt_production"
    qos: 0
    unit_of_measurement: "W"
    value_template: '{% if is_state("sun.sun", "below_horizon")%}0{%else%}{{ value_json["production"]["ph-a"]["p"]  | int(0) }}{%endif%}'
    state_class: measurement
    device_class: power

  - platform: mqtt
    state_topic: "envoy/json"
    value_template: '{{ value_json["total-consumption"]["ph-a"]["p"] }}'
    name: "mqtt_consumption"
    qos: 0
    unit_of_measurement: "W"
    state_class: measurement
    device_class: power

  - platform: mqtt
    state_topic: "envoy/json"
    name: "mqtt_power_factor"
    qos: 0
    unit_of_measurement: "%"
    value_template: '{{ value_json["total-consumption"]["ph-a"]["pf"] }}'
    state_class: measurement
    device_class: power_factor

  - platform: mqtt
    state_topic: "envoy/json"
    name: "mqtt_voltage"
    qos: 0
    unit_of_measurement: "V"
    value_template: '{{ value_json["total-consumption"]["ph-a"]["v"] }}'
    state_class: measurement
    device_class: voltage
#
```
## `configuration.yaml` configuration examples For FW 7
```
mqtt:
  sensor:
    - name: envoy mqtt consumption
      state_topic: "envoy/json"
      value_template: '{{ value_json[1]["activePower"] | round(0) | int(0)}}'
      unique_id: envoy_mqtt_consumption
      qos: 0
      unit_of_measurement: "W"
      state_class: measurement
      device_class: power
    - name: envoy mqtt voltage
      state_topic: "envoy/json"
      value_template: '{{ value_json[1]["voltage"] | round(0) | int(0)}}'
      unique_id: envoy_mqtt_voltage
      qos: 0
      unit_of_measurement: "V"
      state_class: measurement
      device_class: voltage
    - name: envoy mqtt current
      state_topic: "envoy/json"
      value_template: '{{ value_json[1]["current"] | round(2)}}'
      unique_id: envoy_mqtt_current
      qos: 0
      unit_of_measurement: "A"
      state_class: measurement
      device_class: current
    - name: envoy mqtt power factor
      state_topic: "envoy/json"
      value_template: '{{ value_json[1]["pwrFactor"] | round(2)}}'
      unique_id: envoy_mqtt_power_factor
      qos: 0
      unit_of_measurement: "%"
      state_class: measurement
      device_class: power_factor
```

## `value_template` configuration examples for FW5
```yaml
value_template: '{{ value_json["total-consumption"]["ph-a"]["p"] }}' # Phase A Total power consumed by house
value_template: '{{ value_json["net-consumption"]["ph-c"]["p"] }}'   # Phase C - Total Power imported or exported
value_template: '{{ value_json["production"]["ph-b"]["v"] }}'   # Phase B - Voltage produced by panels
value_template: '{{ value_json["production"]["ph-a"]["p"] | int + value_json["production"]["ph-b"]["p"] | int + value_json["production"]["ph-c"]["p"] | int }}'  # Adding all three Production phases

```

## Real time power display using Power Wheel Card

Here's the code if you'd like real-time visualisations of your power usage like this:

<img src="https://www.theshackbythebeach.com/Power-wheel-card.jpeg">

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
    state_topic: "envoy/json"
    name: "mqtt_production"
    qos: 0
    unit_of_measurement: "W"
    value_template: '{% if is_state("sun.sun", "below_horizon")%}0{%else%}{{ value_json["production"]["ph-a"]["p"]  | int(0) }}{%endif%}'
    state_class: measurement
    device_class: power

  - platform: mqtt
    state_topic: "envoy/json"
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
- Configure settings in `/data/options.json`

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

# Example output for FW 5
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
# Example output for FW 7
The resulting mqtt topic should look like this example:
```
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
```
## Donation
If this project helps you, you can give me a cup of coffee<br/>
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/vk2him)
<br/><br/>

