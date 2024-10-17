# Python script: `Enphase Envoy mqtt json for Home Assistant`

A Python script that takes a real time json stream from an Enphase Envoy and publishes to a mqtt broker. This can then be used within Home Assistant or for other applications. The data updates at least once per second with negligible load on the Envoy.

Now works with 7.x.x and 8.x.x firmware - thanks to @helderd

**Note - September 2024 - added ability to utilise Battery data on V7 or V8 firmware (v5 not supported) - to enable, turn on the toggle switch BATTERY_INSTALLED in configuration, then setup templates per Battery examples below - thanks to @Underlyingglitch**

**NOTE - this is a breaking change to your templates if you enable the battery Option**

# Requirements

- An Enphase Envoy running 5.x.x, 7.x.x or 8.x.x firmware.
- For 7.x.x and 8.x.x a token is automatically downloaded from Enphase every time the addon is started, so you must include your Enphase account username and password in configutaion
- A mqtt broker that is already running - this can be external or use the `Mosquitto broker` from the Home Assistant Add-on store
    - If you use the HA broker add-on, create a Home Assistant user/password for mqtt as described in the `Mosquitto broker` installation instructions

# Installation Method 1 - as a Home Assistant addon. ###

1) Add this Repository to your Home Assistant by clicking this button  

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/vk2him/Enphase-Envoy-mqtt-json)

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
## `configuration.yaml` configuration examples For FW 7 and FW 8
This value might needs tweaking based on your firmware.
```yaml
mqtt:
  sensor:
    - name: envoy mqtt consumption
      state_topic: "/envoy/json"
      value_template: '{{ (value_json.meters.load.agg_p_mw| float / 1000) | round(0) | int(0)}}'
      unique_id: envoy_mqtt_consumption
      qos: 0
      unit_of_measurement: "W"
      state_class: measurement
      device_class: power
    - name: envoy mqtt grid
      state_topic: "/envoy/json"
      value_template: '{{ (value_json.meters.grid.agg_p_mw| float / 1000) | round(0) | int(0)}}'
      unique_id: envoy_mqtt_consumption
      qos: 0
      unit_of_measurement: "W"
      state_class: measurement
      device_class: power
    - name: envoy mqtt solar production
      state_topic: "/envoy/json"
      value_template: '{{ (value_json.meters.pv.agg_p_mw| float / 1000) | round(0) | int(0)}}'
      unique_id: envoy_mqtt_consumption
      qos: 0
      unit_of_measurement: "W"
      state_class: measurement
      device_class: power
```

## `configuration.yaml` configuration examples For FW 8 (with batteries)
```yaml
mqtt:
  sensor:
    - name: envoy mqtt consumption
      state_topic: "/envoy/json"
      value_template: '{{ value_json.meters.load.agg_p_mw/1000 | round(0) | int(0) }}'
      unique_id: envoy_mqtt_consumption
      qos: 0
      unit_of_measurement: "W"
      state_class: measurement
      device_class: power
    - name: envoy mqtt production
      state_topic: "/envoy/json"
      value_template: '{{ value_json.meters.pv.agg_p_mw/1000 | round(0) | int(0) }}'
      unique_id: envoy_mqtt_production
      qos: 0
      unit_of_measurement: "W"
      state_class: measurement
      device_class: power
    - name: envoy mqtt battery
      state_topic: "/envoy/json"
      value_template: '{{ value_json.meters.storage.agg_p_mw/1000 | round(0) | int(0) }}'
      unique_id: envoy_mqtt_battery
      qos: 0
      unit_of_measurement: "W"
      state_class: measurement
      device_class: power
```
Available sensors (with example data):
```json
{
...
"meters": {
        "last_update": 1726696114,
        "soc": 86,
        "main_relay_state": 1,
        "gen_relay_state": 5,
        "backup_bat_mode": 2,
        "backup_soc": 6,
        "is_split_phase": 0,
        "phase_count": 3,
        "enc_agg_soc": 86,
        "enc_agg_energy": 8600,
        "acb_agg_soc": 0,
        "acb_agg_energy": 0,
        "pv": {
            "agg_p_mw": -13884,
            "agg_s_mva": -62992,
            "agg_p_ph_a_mw": -6792,
            "agg_p_ph_b_mw": 0,
            "agg_p_ph_c_mw": -7093,
            "agg_s_ph_a_mva": -61120,
            "agg_s_ph_b_mva": 97423,
            "agg_s_ph_c_mva": -99295
        },
        "storage": {
            "agg_p_mw": -6774000,
            "agg_s_mva": -6812225,
            "agg_p_ph_a_mw": -3383000,
            "agg_p_ph_b_mw": -3391000,
            "agg_p_ph_c_mw": 0,
            "agg_s_ph_a_mva": -3329223,
            "agg_s_ph_b_mva": -3489823,
            "agg_s_ph_c_mva": 6820
        },
        "grid": {
            "agg_p_mw": 7585180,
            "agg_s_mva": 7839779,
            "agg_p_ph_a_mw": 3869223,
            "agg_p_ph_b_mw": 3701411,
            "agg_p_ph_c_mw": 14546,
            "agg_s_ph_a_mva": 3869223,
            "agg_s_ph_b_mva": 3723269,
            "agg_s_ph_c_mva": 247286
        },
        "load": {
            "agg_p_mw": 797296,
            "agg_s_mva": 964562,
            "agg_p_ph_a_mw": 479431,
            "agg_p_ph_b_mw": 310411,
            "agg_p_ph_c_mw": 7453,
            "agg_s_ph_a_mva": 478880,
            "agg_s_ph_b_mva": 330869,
            "agg_s_ph_c_mva": 154811
        },
        "generator": {
            "agg_p_mw": 0,
            "agg_s_mva": 0,
            "agg_p_ph_a_mw": 0,
            "agg_p_ph_b_mw": 0,
            "agg_p_ph_c_mw": 0,
            "agg_s_ph_a_mva": 0,
            "agg_s_ph_b_mva": 0,
            "agg_s_ph_c_mva": 0
        }
    },
...
}
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
# Example output for FW 7 and FW 8
The resulting mqtt topic should look like this example:
```
{
    "connection": {
        "mqtt_state": "connected",
        "prov_state": "configured",
        "auth_state": "ok",
        "sc_stream": "enabled",
        "sc_debug": "disabled"
    },
    "meters": {
        "last_update": 1729134820,
        "soc": 0,
        "main_relay_state": 1,
        "gen_relay_state": 5,
        "backup_bat_mode": 1,
        "backup_soc": 30,
        "is_split_phase": 0,
        "phase_count": 1,
        "enc_agg_soc": 0,
        "enc_agg_energy": 0,
        "acb_agg_soc": 0,
        "acb_agg_energy": 0,
        "pv": {
            "agg_p_mw": 2596060,
            "agg_s_mva": 2596060,
            "agg_p_ph_a_mw": 2596060,
            "agg_p_ph_b_mw": 0,
            "agg_p_ph_c_mw": 0,
            "agg_s_ph_a_mva": 2596060,
            "agg_s_ph_b_mva": 0,
            "agg_s_ph_c_mva": 0
        },
        "storage": {
            "agg_p_mw": 0,
            "agg_s_mva": 0,
            "agg_p_ph_a_mw": 0,
            "agg_p_ph_b_mw": 0,
            "agg_p_ph_c_mw": 0,
            "agg_s_ph_a_mva": 0,
            "agg_s_ph_b_mva": 0,
            "agg_s_ph_c_mva": 0
        },
        "grid": {
            "agg_p_mw": -2071260,
            "agg_s_mva": -2151485,
            "agg_p_ph_a_mw": -2071260,
            "agg_p_ph_b_mw": 0,
            "agg_p_ph_c_mw": 0,
            "agg_s_ph_a_mva": -2151485,
            "agg_s_ph_b_mva": 0,
            "agg_s_ph_c_mva": 0
        },
        "load": {
            "agg_p_mw": 524800,
            "agg_s_mva": 444575,
            "agg_p_ph_a_mw": 524800,
            "agg_p_ph_b_mw": 0,
            "agg_p_ph_c_mw": 0,
            "agg_s_ph_a_mva": 444575,
            "agg_s_ph_b_mva": 0,
            "agg_s_ph_c_mva": 0
        },
        "generator": {
            "agg_p_mw": 0,
            "agg_s_mva": 0,
            "agg_p_ph_a_mw": 0,
            "agg_p_ph_b_mw": 0,
            "agg_p_ph_c_mw": 0,
            "agg_s_ph_a_mva": 0,
            "agg_s_ph_b_mva": 0,
            "agg_s_ph_c_mva": 0
        }
    },
    "tasks": {
        "task_id": -1962092090,
        "timestamp": 1729079744
    },
    "counters": {
        "main_CfgLoad": 1,
        "main_CfgChanged": 1,
        "main_taskUpdate": 398,
        "MqttClient_publish": 900,
        "MqttClient_respond": 798,
        "MqttClient_msgarrvd": 399,
        "MqttClient_create": 17,
        "MqttClient_setCallbacks": 17,
        "MqttClient_connect": 17,
        "MqttClient_connect_err": 9,
        "MqttClient_connect_Err": 9,
        "MqttClient_subscribe": 8,
        "SSL_Keys_Create": 17,
        "sc_hdlDataPub": 81096,
        "sc_SendStreamCtrl": 4,
        "sc_SendDemandRspCtrl": 1,
        "rest_Status": 115778
    },
    "dry_contacts": {
        "": {
            "dry_contact_id": "",
            "dry_contact_type": "",
            "dry_contact_load_name": "",
            "dry_contact_status": 3050996
        }
    }
}
```

# Installation Method 3 - In a Docker Container along side your Home Assistant Installation
1. Clone this repository
2. Update data/options.json with the values pertaining to your MQTT and Envoy Installations
3. Run ```docker compose up -d --build --force-recreate```
4. There is no step 4.

## Donation
If this project helps you, you can give me a cup of coffee<br/>
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/vk2him)
<br/><br/>

