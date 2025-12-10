# Deploying to Portainer

This guide covers deploying the Enphase Envoy MQTT bridge using Docker Compose in Portainer.

## Quick Start

### Option 1: Deploy via Portainer UI (Recommended)

1. **Login to Portainer** at `http://your-server:9000`

2. **Navigate to Stacks** → **Add Stack**

3. **Name your stack**: `enphase-envoy`

4. **Build method**: Choose "Git Repository"
   - Repository URL: `https://github.com/JonathanGiles/Enphase-Envoy-mqtt-json`
   - Repository reference: `refs/heads/main`
   - Compose path: `docker-compose.yml`

5. **Or use Web editor**: Copy the contents of `docker-compose.yml` into the editor

6. **Environment variables**: Add these in the Portainer UI (overrides options.json):
   ```
   MQTT_HOST=your.mqtt.broker.ip
   MQTT_PORT=1883
   MQTT_USER=your_mqtt_user
   MQTT_PASSWORD=your_mqtt_password
   MQTT_TOPIC=/envoy/json
   ENVOY_HOST=envoy.local
   ENVOY_USER=your.enphase.email@example.com
   ENVOY_PASSWORD=2e79e47g
   ENVOY_USER_PASS=Q22UuVoCVSqc
   USE_FREEDS=False
   DEBUG=False
   BATTERY_INSTALLED=False
   ```

7. **Deploy the stack**

### Option 2: Deploy via Portainer API/CLI

```bash
# On your local machine, push to your server
cd /Users/jonathan/code/projects/Enphase-Envoy-mqtt-json

# Build and push to your registry (optional)
docker build -f Dockerfile.standalone -t your-registry/enphase-envoy:latest .
docker push your-registry/enphase-envoy:latest

# Or deploy directly via docker-compose
scp -r . your-server:/opt/enphase-envoy/
ssh your-server
cd /opt/enphase-envoy
docker-compose up -d
```

### Option 3: Manual Upload

1. Create a new directory on your server:
   ```bash
   mkdir -p /opt/enphase-envoy/data
   cd /opt/enphase-envoy
   ```

2. Copy these files to the server:
   - `docker-compose.yml`
   - `Dockerfile.standalone`
   - `envoy_to_mqtt_json.py`
   - `requirements.txt`
   - `data/options.json`

3. Start the container:
   ```bash
   docker-compose up -d
   ```

## Configuration

### Using options.json (Default)

The container will read configuration from `data/options.json`. Make sure this file exists with your settings:

```json
{
  "MQTT_HOST": "10.0.0.7",
  "MQTT_USER": "shelly",
  "MQTT_PASSWORD": "shelly",
  "MQTT_PORT": "1883",
  "ENVOY_HOST": "10.0.0.241",
  "ENVOY_USER": "jonathan@jonathangiles.net",
  "ENVOY_PASSWORD": "2e79e47g",
  "ENVOY_USER_PASS": "Q22UuVoCVSqc",
  "USE_FREEDS": "False",
  "MQTT_TOPIC": "/solar/albertstreet/json",
  "DEBUG": "False",
  "BATTERY_INSTALLED": "False"
}
```

### Using Environment Variables (Alternative)

Uncomment the `environment:` section in `docker-compose.yml` and remove or rename `data/options.json`.

You'll need to modify `envoy_to_mqtt_json.py` to read from environment variables instead of the JSON file:

```python
import os

# Replace the options.json loading with:
option_dict = {
    "MQTT_HOST": os.getenv("MQTT_HOST", "localhost"),
    "MQTT_PORT": os.getenv("MQTT_PORT", "1883"),
    "MQTT_USER": os.getenv("MQTT_USER", ""),
    "MQTT_PASSWORD": os.getenv("MQTT_PASSWORD", ""),
    "MQTT_TOPIC": os.getenv("MQTT_TOPIC", "/envoy/json"),
    "ENVOY_HOST": os.getenv("ENVOY_HOST", "envoy.local"),
    "ENVOY_USER": os.getenv("ENVOY_USER", ""),
    "ENVOY_PASSWORD": os.getenv("ENVOY_PASSWORD", ""),
    "ENVOY_USER_PASS": os.getenv("ENVOY_USER_PASS", ""),
    "USE_FREEDS": os.getenv("USE_FREEDS", "False"),
    "DEBUG": os.getenv("DEBUG", "False"),
    "BATTERY_INSTALLED": os.getenv("BATTERY_INSTALLED", "False"),
}
```

## Persistent Data

The `data/` directory is mounted as a volume to persist:
- **token.txt** - Cached Enphase authentication token (renewed automatically)

This prevents the container from re-authenticating with Enphase on every restart.

## Managing the Container

### View Logs
```bash
docker-compose logs -f
# or in Portainer: Stacks → enphase-envoy → Logs
```

### Restart
```bash
docker-compose restart
# or in Portainer: Stacks → enphase-envoy → Stop → Start
```

### Stop
```bash
docker-compose down
# or in Portainer: Stacks → enphase-envoy → Stop
```

### Update
```bash
git pull  # if using git
docker-compose down
docker-compose build --no-cache
docker-compose up -d
# or in Portainer: Stacks → enphase-envoy → Editor → Update the stack
```

### Check Status
```bash
docker-compose ps
# or in Portainer: Containers → enphase-envoy-mqtt
```

## Networking

The container uses `bridge` network mode by default. If your MQTT broker is in another Docker network:

1. Create/use a shared network:
   ```bash
   docker network create home-automation
   ```

2. Modify `docker-compose.yml`:
   ```yaml
   networks:
     - home-automation
   
   networks:
     home-automation:
       external: true
   ```

## Troubleshooting

### Container won't start
- Check logs: `docker-compose logs`
- Verify `data/options.json` exists and is valid JSON
- Ensure MQTT broker is accessible from the container

### Can't connect to MQTT broker
- If using `localhost` or `127.0.0.1`, change to the actual server IP
- If MQTT is in another container, use container name or join same network
- Check firewall rules on MQTT broker

### Token generation fails
- Verify Enphase credentials in `options.json`
- Check you have internet connectivity for Enphase API
- Review logs for specific error messages

### Data not appearing in MQTT
- Test MQTT connection: 
  ```bash
  docker exec enphase-envoy-mqtt python -c \"import socket; print(socket.gethostbyname('your.mqtt.broker.ip'))\"
  ```
- Subscribe to the topic from another client:
  ```bash
  mosquitto_sub -h your.mqtt.broker.ip -p 1883 -u your_mqtt_user -P your_mqtt_password -t /envoy/json
  ```

## Resource Usage

Typical resource usage:
- **CPU**: < 5% (mostly idle, spikes when processing)
- **Memory**: ~50-100 MB
- **Network**: Minimal (small JSON payloads every 1-2 seconds)

## Security Considerations

1. **Credentials**: Consider using Docker secrets or environment variables instead of storing in `options.json`
2. **Network**: Run in an isolated Docker network if possible
3. **MQTT**: Use TLS/SSL for MQTT if broker supports it
4. **Updates**: Keep the base image updated: `docker-compose pull && docker-compose up -d`

## Portainer Stack Template

You can save this as a Portainer App Template:

```json
{
  "type": 3,
  "title": "Enphase Envoy MQTT Bridge",
  "description": "Streams Enphase Envoy solar data to MQTT broker",
  "categories": ["home-automation", "iot"],
  "platform": "linux",
  "logo": "https://enphase.com/sites/default/files/Enphase_Energy_logo.png",
  "repository": {
    "url": "https://github.com/JonathanGiles/Enphase-Envoy-mqtt-json",
    "stackfile": "docker-compose.yml"
  },
  "env": [
    {
      "name": "MQTT_HOST",
      "label": "MQTT Broker Host",
      "default": "localhost"
    },
    {
      "name": "MQTT_PORT",
      "label": "MQTT Broker Port",
      "default": "1883"
    },
    {
      "name": "MQTT_USER",
      "label": "MQTT Username"
    },
    {
      "name": "MQTT_PASSWORD",
      "label": "MQTT Password"
    },
    {
      "name": "MQTT_TOPIC",
      "label": "MQTT Topic",
      "default": "/envoy/json"
    },
    {
      "name": "ENVOY_HOST",
      "label": "Envoy IP Address",
      "default": "envoy.local"
    },
    {
      "name": "ENVOY_USER",
      "label": "Enphase Account Email"
    },
    {
      "name": "ENVOY_USER_PASS",
      "label": "Enphase Account Password"
    }
  ]
}
```

## Benefits of Docker Deployment

✅ **Isolation** - Doesn't interfere with other services
✅ **Portability** - Easy to move between servers
✅ **Auto-restart** - Automatically restarts on failure
✅ **Easy updates** - Just rebuild and redeploy
✅ **Logging** - Centralized log management via Docker
✅ **Resource limits** - Can set CPU/memory limits if needed

## Next Steps

After deployment:
1. Check logs to verify it's working
2. Test MQTT subscription with `mosquitto_sub`
3. Configure OpenHAB (see `openhab/README_OPENHAB.md`)
4. Set up monitoring/alerts in Portainer
