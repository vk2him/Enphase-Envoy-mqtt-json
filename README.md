# Python script: `Enphase Envoy mqtt json for Home Assistant`

A Python script that takes a real time json stream from an Enphase Envoy and publishes to a mqtt broker. This can then be used within Home Assistant or for other applications. The data updates at least once per second with negligible load on the Envoy.

Now works with 7.x.x and 8.x.x firmware - thanks to @helderd

**Note - September 2024 - added ability to utilise Battery data on V7 or V8 firmware (v5 not supported) - to enable, turn on the toggle switch BATTERY_INSTALLED in configuration, then setup templates per Battery examples below - thanks to @Underlyingglitch**

**NOTE - this is a breaking change to your templates if you enable the battery Option**

## Table of Contents

- [Requirements](#requirements)
- [Configuration Variables](#configuration-variables)
- [Installation Methods](#installation-methods)
  - [Method 1: Home Assistant Addon](#installation-method-1---as-a-home-assistant-addon)
  - [Method 2: Docker/Portainer](#installation-method-2---using-docker-and-portainer)
  - [Method 3: Standalone Linux](#installation-method-3---as-a-stand-alone-install-on-a-linux-host)
  - [Method 4: Standalone macOS](#run-automatically-on-macos-as-a-launchagent)
- [Home Assistant Configuration Examples](#configurationyaml-configuration-examples-for-fw-5)
  - [Firmware 5](#configurationyaml-configuration-examples-for-fw-5)
  - [Firmware 7/8](#configurationyaml-configuration-examples-for-fw-7-and-fw-8)
  - [Firmware 8 with Batteries](#configurationyaml-configuration-examples-for-fw-8-with-batteries)
- [Example Output](#example-output-for-fw-5)
- [Power Wheel Card Example](#real-time-power-display-using-power-wheel-card)
- [OpenHAB Integration](#openhab-integration)
- [Additional Resources](#additional-resources)

# Requirements

- An Enphase Envoy running 5.x.x, 7.x.x or 8.x.x firmware.
- For 7.x.x and 8.x.x a token is automatically downloaded from Enphase every time the addon is started, so you must include your Enphase account username and password in configutaion
- A mqtt broker that is already running - this can be external or use the `Mosquitto broker` from the Home Assistant Add-on store
    - If you use the HA broker add-on, create a Home Assistant user/password for mqtt as described in the `Mosquitto broker` installation instructions

# Configuration Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MQTT_HOST` | ✅ Yes | - | MQTT broker hostname/IP address |
| `MQTT_PORT` | No | 1883 | MQTT broker port |
| `MQTT_USER` | ✅ Yes | - | MQTT username |
| `MQTT_PASSWORD` | ✅ Yes | - | MQTT password |
| `MQTT_TOPIC` | No | /envoy/json | MQTT topic to publish to |
| `ENVOY_HOST` | ✅ Yes | - | Envoy IP address |
| `ENVOY_USER` | ✅ Yes | - | Enphase account email |
| `ENVOY_PASSWORD` | No | - | Legacy field (may not be needed) |
| `ENVOY_USER_PASS` | ✅ Yes | - | Enphase account password |
| `USE_FREEDS` | No | False | Enable FreeDS integration |
| `DEBUG` | No | False | Enable debug logging |
| `BATTERY_INSTALLED` | No | False | Set to True if you have Enphase batteries |
| `PUBLISH_INTERVAL` | No | 0 | How often to publish to MQTT in seconds (0 = no delay) |

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
```yaml
mqtt:
  sensor:
    - name: envoy mqtt consumption
      state_topic: "/envoy/json"
      value_template: '{{ value_json[1]["activePower"] | round(0) | int(0)}}'
      unique_id: envoy_mqtt_consumption
      qos: 0
      unit_of_measurement: "W"
      state_class: measurement
      device_class: power
    - name: envoy mqtt voltage
      state_topic: "/envoy/json"
      value_template: '{{ value_json[1]["voltage"] | round(0) | int(0)}}'
      unique_id: envoy_mqtt_voltage
      qos: 0
      unit_of_measurement: "V"
      state_class: measurement
      device_class: voltage
    - name: envoy mqtt current
      state_topic: "/envoy/json"
      value_template: '{{ value_json[1]["current"] | round(2)}}'
      unique_id: envoy_mqtt_current
      qos: 0
      unit_of_measurement: "A"
      state_class: measurement
      device_class: current
    - name: envoy mqtt power factor
      state_topic: "/envoy/json"
      value_template: '{{ value_json[1]["pwrFactor"] | round(2)}}'
      unique_id: envoy_mqtt_power_factor
      qos: 0
      unit_of_measurement: "%"
      state_class: measurement
      device_class: power_factor
```

## `configuration.yaml` configuration examples For FW 8 (with batteries)
```yaml
mqtt:
  sensor:
    - name: envoy mqtt consumption
      state_topic: "/envoy/json"
      value_template: '{{ value_json["meters"]["grid"]["agg_p_mw"]/1000 | round(0) | int(0) }}'
      unique_id: envoy_mqtt_consumption
      qos: 0
      unit_of_measurement: "W"
      state_class: measurement
      device_class: power
    - name: envoy mqtt production
      state_topic: "/envoy/json"
      value_template: '{{ value_json["meters"]["pv"]["agg_p_mw"]/1000 | round(0) | int(0) }}'
      unique_id: envoy_mqtt_production
      qos: 0
      unit_of_measurement: "W"
      state_class: measurement
      device_class: power
    - name: envoy mqtt battery
      state_topic: "/envoy/json"
      value_template: '{{ value_json["meters"]["storage"]["agg_p_mw"]/1000 | round(0) | int(0) }}'
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
## `Templating examples` 

 View this thread for Additional templating examples https://github.com/vk2him/Enphase-Envoy-mqtt-json/issues/42
 
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

### December 2025 - PLEASE NOTE !!!
#
#   If you have an existing template: entry in your configuration.yaml, add the following code WITHOUT the template: line as you are only allowed one template: in your configuration.yaml . Also ensure the added lines align correctly with other entries in that template: section

template:
  - sensor:
    - unit_of_measurement: W
      default_entity_id: sensor.exporting_mqtt
      icon: mdi:flash
      name: Current MQTT Energy Exporting
      state: '{{ [0, (states(''sensor.mqtt_production'') | int(0) - states(''sensor.mqtt_consumption'')
        | int(0))] | max }}'

  - sensor:
    - unit_of_measurement: W
      default_entity_id: sensor.importing_mqtt
      icon: mdi:flash
      name: Current MQTT Energy Importing
      state: '{{ [0, (states(''sensor.mqtt_consumption'') | int(0) - states(''sensor.mqtt_production'')
        | int(0))] | max }}'

  - sensor:
    - unit_of_measurement: W
      default_entity_id: sensor.solarpower_mqtt
      icon: mdi:flash
      name: Solar MQTT Power
      state: '{{ states(''sensor.mqtt_production'')}}'

```

# Installation Method 3 - as a stand-alone install on a Linux host

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

# Installation Method 2 - Using Docker and Portainer

### Option 1: Using Portainer Environment Variables (Recommended)

1. In Portainer: **Stacks → Add Stack** → Name it `enphase-envoy`

2. **Repository:** Choose "Git Repository"
   - URL: `https://github.com/YOUR-USERNAME/Enphase-Envoy-mqtt-json`
   - Reference: `refs/heads/main`
   - Compose path: `docker-compose.yml`

3. **Add Environment Variables** in the stack editor:
   ```
   MQTT_HOST=your.mqtt.broker.ip
   MQTT_PORT=1883
   MQTT_USER=your_mqtt_user
   MQTT_PASSWORD=your_mqtt_password
   MQTT_TOPIC=/envoy/json
   ENVOY_HOST=envoy.local
   ENVOY_USER=your.enphase.email@example.com
   ENVOY_PASSWORD=legacy_field
   ENVOY_USER_PASS=your_enphase_password
   USE_FREEDS=False
   DEBUG=False
   BATTERY_INSTALLED=False
   PUBLISH_INTERVAL=0
   ```

4. **Deploy the stack**

### Option 2: Upload with .env file

1. Create your `.env` file on the server:
   ```bash
   ssh your-server
   mkdir -p /opt/enphase-envoy
   cd /opt/enphase-envoy
   
   # Create .env file
   cat > .env << 'EOF'
   MQTT_HOST=your.mqtt.broker.ip
   MQTT_PORT=1883
   MQTT_USER=your_mqtt_user
   MQTT_PASSWORD=your_mqtt_password
   MQTT_TOPIC=/envoy/json
   ENVOY_HOST=envoy.local
   ENVOY_USER=your.enphase.email@example.com
   ENVOY_PASSWORD=legacy_field
   ENVOY_USER_PASS=your_enphase_password
   USE_FREEDS=False
   DEBUG=False
   BATTERY_INSTALLED=False
   PUBLISH_INTERVAL=0
   EOF
   ```

2. Copy the docker-compose.yml to the same directory

3. In Portainer: **Stacks → Add Stack → Upload**
   - Upload the `docker-compose.yml`
   - Or point to `/opt/enphase-envoy`

## Persistent Data

The container uses a named volume `enphase-data` to store:
- **token.txt** - Cached Enphase authentication token (auto-renewed)

This persists across container restarts and updates.

## Testing

### Test MQTT subscription:
```bash
mosquitto_sub -h your.mqtt.broker.ip -p 1883 -u your_mqtt_user -P your_mqtt_password -t /envoy/json -v
```

### Check container logs:
```bash
docker-compose logs -f enphase-envoy
```

### Verify container is running:
```bash
docker-compose ps
```

## Updating

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

In Portainer: **Stacks → enphase-envoy → Pull and redeploy**

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

# OpenHAB Integration

For OpenHAB users, complete integration files are available in the `openhab/` directory:

- **solar.things** - MQTT Thing definition with channels for all Envoy data points
- **solar.items** - 40+ items including power, energy, and calculated values
- **solar.rules** - Automation rules for calculations, alerts, and smart home integration
- **solar.sitemap** - UI configuration for displaying solar data
- **README_OPENHAB.md** - Complete setup instructions

See [openhab/README_OPENHAB.md](openhab/README_OPENHAB.md) for detailed installation and configuration instructions.

# Additional Resources

- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference guide for Docker/Portainer deployment
- **[openhab/](openhab/)** - Complete OpenHAB integration with Things, Items, Rules, and Sitemap
- **Configuration Files:**
  - `config.yaml` - Home Assistant addon configuration
  - `docker-compose.yml` - Docker Compose configuration
  - `.env.example` - Environment variable template

## Donation

If this project helps you, you can give me a cup of coffee<br/>
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/vk2him)
<br/><br/>

