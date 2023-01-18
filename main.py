#!/bin/python3

from decouple import config
import json
import co2meter as co2
import hid
import time
from datetime import datetime
import paho.mqtt.publish as publish

def send_via_mqtt(topic, payload, retain = False):
    username = config("MQTT_BROKER_USERNAME", default = None)
    password = config("MQTT_BROKER_PASSWORD", default = None)
    auth = dict()
    if username is not None:
        auth["username"] = username
    if password is not None:
        auth["password"] = password
    hostname = config("MQTT_BROKER_HOSTNAME", default="localhost")
    port = config("MQTT_BROKER_PORT", default = 1883, cast = int)
    

    authentication_info = f"user: {username}, password: {'*' * len(password)}"
    print(f"Sending via {hostname}:{port} ({authentication_info}) in topic '{topic}': {payload}")
    publish.single(hostname = hostname,
                   port = port,
                   auth = auth,
                   qos = 0,
                   retain = retain,
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
    send_via_mqtt(topic = co2_config_topic, payload = json.dumps(co2_config_payload),
                  retain = True)
    
    temperature_config_payload = {
            "device_class": "temperature",
            "name": "Temperature",
            "state_topic": state_topic,
            "unit_of_measurement": "°C",
            "value_template": "{{value_json.temperature}}"
            }
    send_via_mqtt(topic = temperature_config_topic,
                  payload = json.dumps(temperature_config_payload), retain = True)
    
    while True:
        data = mon.read_data()
        print(data)
        
        (_, co2_in_ppm, temperature) = data
        payload = {"co2_in_ppm": co2_in_ppm, "temperature": round(temperature, 1)}
        send_via_mqtt(topic = state_topic, payload = json.dumps(payload))
        
        wait_duration = 10
        print(f"Waiting for {wait_duration} seconds..", flush=True)
        time.sleep(wait_duration)

run()
print()
