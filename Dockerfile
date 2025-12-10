ARG BUILD_FROM=python:3.12-alpine
FROM $BUILD_FROM

# Set working directory
WORKDIR /app

# Install requirements
RUN apk add --no-cache python3 py3-pip && \
    pip install --no-cache-dir paho-mqtt requests urllib3

# Copy application files
COPY envoy_to_mqtt_json.py .
COPY run.sh /run.sh

# Create data directory
RUN mkdir -p /app/data && chmod a+x /run.sh

# For standalone use, run directly; for HA addon, use run.sh
CMD [ "python3", "-u", "envoy_to_mqtt_json.py" ]