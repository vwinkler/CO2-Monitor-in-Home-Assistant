# CO2 Monitor in Home Assistant
A program that connects the USB "CO2-Monitor AIRCO2NTROL MINI 31.5006" to Home Assistant.

![Home Assistant Dashboard Card with CO2 level in ppm and tmperature in °C](https://user-images.githubusercontent.com/8530711/213558555-05907544-2f2f-4e4d-bd03-84001517e2d9.png)

## Requirements
* The USB CO2 device plugged into a device with Docker
* A running instance of Home Assistant [connected to an MQTT broker](https://www.home-assistant.io/integrations/mqtt)

## Usage
Build the Docker image via
```
docker build . -t ha-co2meter
```
and run it via
```
docker run \
--privileged \
--detach \
--restart always \
--env HOMEASSISTANT_OBJECT_ID=co2monitor_0 \
--env MQTT_BROKER_HOSTNAME=192.168.188.111 \
--env MQTT_BROKER_USERNAME=username \
--env MQTT_BROKER_PASSWORD=password \
ha-co2meter
```
Replace the IP address with the IP address of theMQTT broker (or use Home Assistant's IP address if you are using the
[Mosquitto add-on](https://github.com/home-assistant/addons/blob/master/mosquitto/DOCS.md))
and set the username and the password to one the broker will accept (or remove the options if there is no passwod and/or username).
Make sure the USB device is plugged in.

There may be ways to avoid privileging the container.
They have not yet been tested.

## Behavior
At startup the program sends configurations for the CO2 and the temperature entities
as part of the [MQTT discovery](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery).
Then it keeps reading the CO2 level and the temperature from the USB device and sends them to Home Assistant.

All attempts to send messages and are logged.
If an error occurs (e.g. unable to connect to the USB device or Home Assistant) it is logged and the program terminates.
The above Docker command will then restart the container,
thus the program should resume after restarting the program or Home Assistant or plugging the USB device out and back in.

## Configuration
The following environment variables may/must be set.
| Variable                       | Mandatory | Default   | Meaning |
|--------------------------------|-----------|-----------|---------
| HOMEASSISTANT_OBJECT_ID        | yes       | -         | used by Home Assistant ([see here](https://www.home-assistant.io/docs/configuration/state_object/))
| MQTT_BROKER_HOSTNAME           | no        | localhost | hostname of the MQTT broker
| MQTT_BROKER_PORT               | no        | 1883      | port listened to by the MQTT broker
| MQTT_BROKER_USERNAME           | no        | -         | username to authenticate with the MQTT broker
| MQTT_BROKER_PASSWORD           | no        | -         | password to authenticate with the MQTT broker
