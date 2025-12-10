# Standalone Installation (Linux/macOS)

This guide covers running the Enphase Envoy MQTT bridge as a standalone Python script on Linux or macOS systems.

## Prerequisites

- Python 3.x installed
- Git (for cloning the repository)
- Access to a terminal/command line

## Installation Steps

1. Clone the repository to your system:

   ```bash
   git clone https://github.com/vk2him/Enphase-Envoy-mqtt-json
   cd Enphase-Envoy-mqtt-json
   ```

2. Install required Python packages:

   ```bash
   pip install paho-mqtt
   ```

   If that doesn't work, try:

   ```bash
   git clone https://github.com/eclipse/paho.mqtt.python
   cd paho.mqtt.python
   python setup.py install
   ```

3. Configure settings in `/data/options.json`

## Running Manually

To run the script manually:

```bash
/path/to/python3 /path/to/envoy_to_mqtt_json.py
```

## Running Automatically

### Linux (systemd)

This should work for any Linux distribution that uses systemd services (Ubuntu, Debian, Mint, Fedora, etc.), though locations may vary slightly.

1. Note the path to your Python executable and the script:

   ```bash
   which python3
   # Example: /usr/bin/python3
   
   pwd
   # Note the full path to envoy_to_mqtt_json.py
   ```

2. Create a systemd service file:

   ```bash
   cd /etc/systemd/system
   sudo nano envoy.service
   ```

3. Add the following configuration (update `User`, `Group`, and paths):

   ```ini
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

4. Enable and start the service:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable envoy.service
   sudo systemctl start envoy.service
   ```

5. Check the status:

   ```bash
   systemctl status envoy
   ```

### macOS (LaunchAgent)

1. Create a LaunchAgent plist file:

   ```bash
   nano ~/Library/LaunchAgents/envoy.plist
   ```

2. Add the following configuration (update paths):

   ```xml
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

3. Load the LaunchAgent:

   ```bash
   launchctl load ~/Library/LaunchAgents/envoy.plist
   ```

4. To stop the service:

   ```bash
   launchctl unload ~/Library/LaunchAgents/envoy.plist
   ```

## Troubleshooting

- **Service won't start**: Check logs with `journalctl -u envoy -f` (Linux) or `log stream --predicate 'processImagePath contains "python"'` (macOS)
- **Python module not found**: Ensure paho-mqtt is installed in the correct Python environment
- **Permission denied**: Make sure the script has execute permissions: `chmod +x envoy_to_mqtt_json.py`
