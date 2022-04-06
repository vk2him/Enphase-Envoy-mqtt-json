ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on

RUN apk add --no-cache python3 py3-requests py3-pip py3-paho-mqtt

# Copy data for add-on
COPY run.sh /
COPY envoy_to_mqtt_json.py /

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]