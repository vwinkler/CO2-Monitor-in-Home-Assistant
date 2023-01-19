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
