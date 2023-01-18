#!/bin/python3

import sys
from dataclasses import dataclass
from decouple import config
import json
import co2meter as co2
import hid
import time
import paho.mqtt.publish as publish


class MqttBroker:
    def __init__(self, hostname, port, auth):
        self.hostname = hostname
        self.port = port
        self.auth = auth

    def send(self, topic, payload, retain=False):
        print(self.make_sending_log_line(topic, payload))
        publish.single(hostname=self.hostname,
                       port=self.port,
                       auth=self.auth,
                       qos=0,
                       retain=retain,
                       topic=topic,
                       payload=payload)

    def make_sending_log_line(self, topic, payload):
        auth_info = self.make_auth_log_string()
        result = f"Sending via {self.hostname}:{self.port} ({auth_info})\n"
        result += f"  in topic '{topic}':\n"
        result += f"  {payload}"
        return result

    def make_auth_log_string(self):
        username = self.make_username_log_string()
        password = self.make_censored_password_log_string()
        return f"user: {username}, password: {password}"

    def make_censored_password_log_string(self):
        if "password" in self.auth:
            return "*" * len(self.auth["password"])
        else:
            return "undefined"

    def make_username_log_string(self):
        if "username" in self.auth:
            return self.auth["username"]
        else:
            return "undefined"


class HomeAssistantObject:
    def __init__(self, object_id: str):
        self.object_id = object_id

    def get_co2_sensor_config_topic(self):
        return f"homeassistant/sensor/{self.object_id}_co2/config"

    def get_temperature_sensor_config_topic(self):
        return f"homeassistant/sensor/{self.object_id}_temperature/config"

    def get_object_state_topic(self):
        return f"homeassistant/sensor/{self.object_id}/state"

    def get_co2_sensor_config_payload(self):
        return {
            "device_class": "carbon_dioxide",
            "name": "CO2",
            "state_topic": self.get_object_state_topic(),
            "unit_of_measurement": "ppm",
            "value_template": "{{value_json.co2_in_ppm}}"
        }

    def get_temperature_sensor_config_payload(self):
        return {
            "device_class": "temperature",
            "name": "Temperature",
            "state_topic": self.get_object_state_topic(),
            "unit_of_measurement": "°C",
            "value_template": "{{value_json.temperature}}"
        }


@dataclass(frozen=True)
class Status:
    co2_in_ppm: int
    temperature_in_celsius: float


class Co2MonitorSender:
    def __init__(self, broker: MqttBroker, ha_object: HomeAssistantObject):
        self.broker = broker
        self.ha_object = ha_object

    def send_co2_sensor_configuration(self):
        payload = json.dumps(self.ha_object.get_co2_sensor_config_payload())
        self.broker.send(topic=self.ha_object.get_co2_sensor_config_topic(),
                         payload=payload, retain=True)

    def send_temperature_sensor_configuration(self):
        payload = json.dumps(
                self.ha_object.get_temperature_sensor_config_payload())
        self.broker.send(
                topic=self.ha_object.get_temperature_sensor_config_topic(),
                payload=payload, retain=True)

    def send_status(self, status: Status):
        payload = {"co2_in_ppm": status.co2_in_ppm,
                   "temperature": round(status.temperature_in_celsius, 1)}
        self.broker.send(topic=self.ha_object.get_object_state_topic(),
                         payload=json.dumps(payload))


def run():
    monitor = connect_to_monitor()
    log_co2_monitor_info(monitor)
    sender = create_sender_from_environment()
    sender.send_co2_sensor_configuration()
    sender.send_temperature_sensor_configuration()

    while True:
        status = read_status(monitor)
        sender.send_status(status)
        wait_before_next_update()


def connect_to_monitor() -> co2.CO2monitor:
    try:
        return co2.CO2monitor()
    except Exception:
        print_monitor_access_error()
        raise


def print_monitor_access_error():
    print("Could not reach co2meter via usb. Aborting")

    devices = hid.enumerate()
    print(f"Found {len(devices)} HID devices:")
    for i, device in enumerate(devices):
        print(f"  Device {i}: {device}")
    sys.stdout.flush()


def log_co2_monitor_info(monitor: co2.CO2monitor):
    print(monitor.info)


def create_sender_from_environment() -> Co2MonitorSender:
    hostname = config("MQTT_BROKER_HOSTNAME", default="localhost")
    port = config("MQTT_BROKER_PORT", default=1883, cast=int)
    auth = get_mqtt_auth_from_environment()
    broker = MqttBroker(hostname, port, auth)
    ha_object = HomeAssistantObject(config("HOMEASSISTANT_OBJECT_ID"))
    return Co2MonitorSender(broker, ha_object)


def get_mqtt_auth_from_environment() -> dict:
    username = config("MQTT_BROKER_USERNAME", default=None)
    password = config("MQTT_BROKER_PASSWORD", default=None)
    auth = dict()
    if username is not None:
        auth["username"] = username
    if password is not None:
        auth["password"] = password
    return auth


def read_status(monitor: co2.CO2monitor) -> Status:
    (_, co2_in_ppm, temperature_in_celsius) = monitor.read_data()
    return Status(co2_in_ppm, temperature_in_celsius)


def wait_before_next_update():
    wait_duration = 10
    print(f"Waiting for {wait_duration} seconds..", flush=True)
    time.sleep(wait_duration)


run()
print()
