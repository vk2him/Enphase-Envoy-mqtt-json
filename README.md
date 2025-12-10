# Enphase Envoy MQTT State Publisher

A Python script that takes a real time json stream from an Enphase Envoy and publishes to a mqtt broker. This can then be used within Home Assistant or for other applications. The data updates at least once per second with negligible load on the Envoy.

Now works with 7.x.x and 8.x.x firmware - thanks to @helderd

> [!NOTE]
> **September 2024** - Added ability to utilise Battery data on V7 or V8 firmware (v5 not supported). To enable, turn on the toggle switch BATTERY_INSTALLED in configuration, then setup templates per Battery examples - thanks to @Underlyingglitch

> [!WARNING]
> This is a breaking change to your templates if you enable the battery Option

## Table of Contents

- [Requirements](#requirements)
- [Configuration Variables](#configuration-variables)
- Installation Methods
  - [Method 1: Home Assistant Addon](#installation-method-1---as-a-home-assistant-addon)
  - [Method 2: Standalone Linux/macOS](STANDALONE.md)
  - [Method 3: Docker/Portainer](PORTAINER.md)
- [Home Assistant Configuration](HOME-ASSISTANT.md)
- [Example Output](#example-output)
- [OpenHAB Integration](#openhab-integration)
- [Additional Resources](#additional-resources)

## Requirements

- An Enphase Envoy running 5.x.x, 7.x.x or 8.x.x firmware.
- For 7.x.x and 8.x.x a token is automatically downloaded from Enphase every time the addon is started, so you must include your Enphase account username and password in configutaion
- A mqtt broker that is already running - this can be external or use the `Mosquitto broker` from the Home Assistant Add-on store
  - If you use the HA broker add-on, create a Home Assistant user/password for mqtt as described in the `Mosquitto broker` installation instructions

## Configuration Variables

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

## Installation Method 1 - as a Home Assistant addon.

For detailed Home Assistant configuration examples (including FW5, FW7/8, FW8 with batteries, templates, and Power Wheel Card setup), see **[HOME-ASSISTANT.md](HOME-ASSISTANT.md)**.

## Installation Method 2 - Standalone Installation (Linux/macOS)

For standalone installation instructions (including systemd service setup for Linux and LaunchAgent setup for macOS), see **[STANDALONE.md](STANDALONE.md)**.

## Installation Method 3 - Using Docker/Portainer

For detailed Docker and Portainer deployment instructions (including environment variable configuration, .env file setup, testing, and updating), see **[PORTAINER.md](PORTAINER.md)**.

## Example Output

### Example output for FW 5

The resulting mqtt topic should look like this example:

```json
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

> [!NOTE]
> Data is provided for three phases - unused phases have values of `0.0`

#### Description of labels

More info here: https://www.greenwoodsolutions.com.au/news-posts/real-apparent-reactive-power

- **`"production"`** = Solar panel production - always positive value
- **`"total-consumption"`** = Total Power consumed - always positive value
- **`"net-consumption"`** = Total power Consumed minus Solar panel production. Will be positive when importing and negative when exporting

**Phase labels:**

- `"ph-a"` = Phase A
- `"ph-b"` = Phase B
- `"ph-c"` = Phase C

**Measurement labels:**

- `"p"` = Real Power ⭐ **This is the one to use**
- `"q"` = Reactive Power
- `"s"` = Apparent Power
- `"v"` = Voltage
- `"i"` = Current
- `"pf"` = Power Factor
- `"f"` = Frequency

### Example output for FW 7 and FW 8

The resulting mqtt topic should look like this example:

```json
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
]
```

## OpenHAB Integration

For OpenHAB users, complete integration files are available in the `openhab/` directory:

- **solar.things** - MQTT Thing definition with channels for all Envoy data points
- **solar.items** - 40+ items including power, energy, and calculated values
- **solar.rules** - Automation rules for calculations, alerts, and smart home integration
- **solar.sitemap** - UI configuration for displaying solar data
- **README_OPENHAB.md** - Complete setup instructions

See [openhab/README_OPENHAB.md](openhab/README_OPENHAB.md) for detailed installation and configuration instructions.

## Additional Resources

- **[openhab/](openhab/)** - Complete OpenHAB integration with Things, Items, Rules, and Sitemap
- **Configuration Files:**
  - `config.yaml` - Home Assistant addon configuration
  - `docker-compose.yml` - Docker Compose configuration
  - `.env.example` - Environment variable template

## Donation

If this project helps you, you can give me a cup of coffee: [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/vk2him)
