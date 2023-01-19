#!/bin/python3

import json

from . import MqttBroker, HomeAssistantObject, Status


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
