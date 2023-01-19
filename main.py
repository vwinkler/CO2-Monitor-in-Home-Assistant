#!/bin/python3

import sys
from decouple import config
import co2meter as co2
import hid
import time
from src import MqttBroker, HomeAssistantObject, Co2MonitorSender, Status


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
