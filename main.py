#!/bin/python3

from decouple import config
import json
import co2meter as co2
import hid
import time
from datetime import datetime
import paho.mqtt.publish as publish

def send_via_mqtt(topic, payload):
    username = config("MQTT_BROKER_USERNAME", default = None)
    password = config("MQTT_BROKER_PASSWORD", default = None)
    auth = dict()
    if username is not None:
        auth["username"] = username
    if password is not None:
        auth["password"] = password
    hostname = config("MQTT_BROKER_HOSTNAME", default="localhost")
    port = config("MQTT_BROKER_PORT", default = 1883, cast = int)
    
    print(f"Sending via {hostname}:{port} (authentication = {auth}) in topic '{topic}': {payload}")
    publish.single(hostname = hostname,
                   port = port,
                   auth = auth,
                   qos = 0,
                   topic = topic,
                   payload = payload)

def run():
    try:
        mon = co2.CO2monitor()
    except Exception as e:
        print(e)
        print("Could not reach co2meter via usb. Aborting")
        
        devices = hid.enumerate()
        print(f"Found {len(devices)} HID devices:")
        for i, device in enumerate(devices):
            print(f"  Device {i}: {device}")
        return

    print(mon.info)
    
    object_id = config("HOMEASSISTANT_OBJECT_ID")
    
    co2_config_topic = f"homeassistant/sensor/{object_id}_co2/config"
    temperature_config_topic = f"homeassistant/sensor/{object_id}_temperature/config"
    state_topic = f"homeassistant/sensor/{object_id}/state"
    
    co2_config_payload = {
            "device_class": "carbon_dioxide",
            "name": "CO2",
            "state_topic": state_topic,
            "unit_of_measurement": "ppm",
            "value_template": "{{value_json.co2_in_ppm}}"
            }
    send_via_mqtt(topic = co2_config_topic, payload = json.dumps(co2_config_payload))
    
    temperature_config_payload = {
            "device_class": "temperature",
            "name": "Temperature",
            "state_topic": state_topic,
            "unit_of_measurement": "°C",
            "value_template": "{{value_json.temperature}}"
            }
    send_via_mqtt(topic = temperature_config_topic,
                  payload = json.dumps(temperature_config_payload))
    
    while True:
        data = mon.read_data()
        print(data, flush=True)
        
        (_, co2_in_ppm, temperature) = data
        payload = {"co2_in_ppm": co2_in_ppm, "temperature": temperature}
        send_via_mqtt(topic = state_topic, payload = json.dumps(payload))
        time.sleep(10)

run()
print()
