# Quick Start Guide

## Local Development with .env

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your actual values:**
   ```bash
   nano .env
   # or use your favorite editor
   ```

3. **Start the container:**
   ```bash
   docker-compose up -d
   ```

4. **View logs:**
   ```bash
   docker-compose logs -f
   ```

## Portainer Deployment

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


