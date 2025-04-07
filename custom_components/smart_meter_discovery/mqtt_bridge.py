import paho.mqtt.client as mqtt
import json
from datetime import datetime

def start_bridge(config):
    SOURCE_BROKER = config.get("source_broker")
    SOURCE_PORT = config.get("source_port", 8883)
    SOURCE_USERNAME = config.get("source_user")
    SOURCE_PASSWORD = config.get("source_pass")
    SOURCE_TOPIC = config.get("source_topic")

    TARGET_BROKER = config.get("target_broker")
    TARGET_PORT = config.get("target_port", 1883)
    TARGET_USERNAME = config.get("target_user")
    TARGET_PASSWORD = config.get("target_pass")
    TARGET_TOPIC = config.get("target_topic")

    target_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if TARGET_USERNAME and TARGET_PASSWORD:
        target_client.username_pw_set(TARGET_USERNAME, TARGET_PASSWORD)
    target_client.connect(TARGET_BROKER, TARGET_PORT, 300)
    target_client.loop_start()

    def publish_discovery_configs(data_dict):
        for key, value in data_dict.items():
            sensor_id = key.lower()
            discovery_topic = f"homeassistant/sensor/smart_meter_{sensor_id}/config"
            discovery_payload = {
                "name": f"Smart Meter {key}",
                "state_topic": TARGET_TOPIC,
                "value_template": f"{{{{ value_json.{key} }}}}",
                "unique_id": f"smart_meter_{sensor_id}_sensor",
                "device": {
                    "identifiers": ["smart_meter_bridge_device"],
                    "name": "Smart Meter",
                    "manufacturer": "IKB Telekommunikation",
                    "model": "Meter2Lora_V2_Profile"
                },
                "object_id": f"smart_meter_{sensor_id}",
                "friendly_name": f"Smart Meter {key}"
            }

            if "voltage" in sensor_id:
                discovery_payload.update({"unit_of_measurement": "V", "device_class": "voltage", "icon": "mdi:flash", "state_class": "measurement"})
            elif "current" in sensor_id:
                discovery_payload.update({"unit_of_measurement": "A", "device_class": "current", "icon": "mdi:current-ac", "state_class": "measurement"})
            elif "power" in sensor_id:
                discovery_payload.update({"unit_of_measurement": "W", "device_class": "power", "icon": "mdi:lightning-bolt", "state_class": "measurement"})
            elif "energy" in sensor_id:
                discovery_payload.update({
                    "unit_of_measurement": "Wh",
                    "device_class": "energy",
                    "icon": "mdi:transmission-tower",
                    "state_class": "total_increasing",
                    "last_reset": "1970-01-01T00:00:00+00:00"
                })

            target_client.publish(discovery_topic, json.dumps(discovery_payload), qos=1, retain=True)

    def on_message(client, userdata, message):
        payload = message.payload.decode("utf-8")
        try:
            payload_json = json.loads(payload)
            object_data = payload_json.get("object", {})
            if isinstance(object_data, dict) and object_data:
                target_client.publish(TARGET_TOPIC, json.dumps(object_data), qos=1, retain=True)
                publish_discovery_configs(object_data)
        except json.JSONDecodeError:
            pass

    def on_connect_source(client, userdata, flags, rc, properties=None):
        if rc == 0:
            client.subscribe(SOURCE_TOPIC, qos=1)

    source_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    source_client.username_pw_set(SOURCE_USERNAME, SOURCE_PASSWORD)
    source_client.tls_set()
    source_client.on_connect = on_connect_source
    source_client.on_message = on_message
    source_client.connect(SOURCE_BROKER, SOURCE_PORT, 300)
    source_client.loop_start()
