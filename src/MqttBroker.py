#!/bin/python3

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
