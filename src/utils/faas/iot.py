import json
import websockets
import paho.mqtt.client as paho
from paho import mqtt
from utils.logger import log_msg
from utils.common import is_not_empty_key, create_file_locally, delete_file_locally

async def send_websocket_payload(uri, payload):
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(payload))

def on_connect(client, userdata, flags, rc, properties=None):
    log_msg("DEBUG", "[on_connect] CONNACK received with code %s." % rc)

def on_publish(client, userdata, mid, properties=None):
    log_msg("DEBUG", "[on_publish] mid: {}".format(str(mid)))

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    log_msg("DEBUG", "[on_subscribe] Subscribed: {} {}".format(str(mid), str(granted_qos)))

def on_message(client, userdata, msg):
    log_msg("DEBUG", "[on_message] topic: {} qos: {} payload: {}".format(msg.topic, str(msg.qos), str(msg.payload)))

async def send_mqtt_payload(callback, mqtt_payload):
    client_id = callback['client_id'] if is_not_empty_key(callback, 'client_id') else ""
    user_data = callback['user_data'] if is_not_empty_key(callback, 'user_data') else None
    username = callback['username'] if is_not_empty_key(callback, 'username') else ""
    password = callback['password'] if is_not_empty_key(callback, 'password') else ""
    endpoint = callback['endpoint'] if is_not_empty_key(callback, 'endpoint') else ""
    port = int(callback['port']) if is_not_empty_key(callback, 'port') else 8883
    subscription = callback['subscription'] if is_not_empty_key(callback, 'subscription') else "faas/#"
    qos = int(callback['qos']) if is_not_empty_key(callback, 'qos') else 1
    topic = callback['topic'] if is_not_empty_key(callback, 'topic') else "faas/test"
    certificates_are_required = callback['certificates_are_required'] if is_not_empty_key(callback, 'certificates_are_required') else False
    certificates = callback['certificates'] if is_not_empty_key(callback, 'certificates') else None

    client = paho.Client(client_id=client_id, userdata=user_data, protocol=paho.MQTTv5)
    client.on_connect = on_connect
    if certificates_are_required:
        create_file_locally("iot_hub_certificate", certificates['iot_hub_certificate'])
        create_file_locally("device_certificate", certificates['device_certificate'])
        create_file_locally("device_key_certificate", certificates['device_key_certificate'])
        client.tls_set(
            ca_certs="./iot_hub_certificate.pem",
            certfile="./device_certificate.pem",
            keyfile="./device_key_certificate.pem",
            tls_version=mqtt.client.ssl.PROTOCOL_TLS
        )
    else:
        client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.username_pw_set(username, password)
    client.connect(endpoint, port)
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_publish = on_publish
    client.subscribe(subscription, qos=qos)
    client.publish(topic, payload=json.dumps(mqtt_payload), qos=qos)
    if certificates_are_required:
        delete_file_locally("iot_hub_certificate")
        delete_file_locally("device_certificate")
        delete_file_locally("device_key_certificate")
    # client.loop_forever()
