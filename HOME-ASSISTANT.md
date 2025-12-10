# Home Assistant Add-on Installation Instructions

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

## Home Assistant Configuration Examples

This file contains configuration examples for integrating Enphase Envoy data with Home Assistant.

### `configuration.yaml` configuration examples For FW 5

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

### `configuration.yaml` configuration examples For FW 7 and FW 8

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

### `configuration.yaml` configuration examples For FW 8 (with batteries)

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

### `value_template` configuration examples for FW5

```yaml
value_template: '{{ value_json["total-consumption"]["ph-a"]["p"] }}' # Phase A Total power consumed by house
value_template: '{{ value_json["net-consumption"]["ph-c"]["p"] }}'   # Phase C - Total Power imported or exported
value_template: '{{ value_json["production"]["ph-b"]["v"] }}'   # Phase B - Voltage produced by panels
value_template: '{{ value_json["production"]["ph-a"]["p"] | int + value_json["production"]["ph-b"]["p"] | int + value_json["production"]["ph-c"]["p"] | int }}'  # Adding all three Production phases
```

### `Templating examples` 

View this thread for Additional templating examples https://github.com/vk2him/Enphase-Envoy-mqtt-json/issues/42
 
### Real time power display using Power Wheel Card

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

> [!IMPORTANT]
> If you have an existing `template:` entry in your configuration.yaml, add the following code WITHOUT the `template:` line as you are only allowed one `template:` in your configuration.yaml. Also ensure the added lines align correctly with other entries in that `template:` section.

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
