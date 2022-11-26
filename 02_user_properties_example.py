# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from paho.mqtt.packettypes import PacketTypes
import ssl
import time
from paho.mqtt.properties import Properties
import paho.mqtt.client as mqtt
import logging
import base64
import argparse

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('--endpoint', dest='endpoint', type=str, required=True, help='Obtain your Device data endpoint for your AWS Account')
parser.add_argument('--certificates-path', dest='certificates_path', default='certificates', 
                    type=str, required=False, help='Modify the cert folder path if your certificates are in another folder')

args = parser.parse_args()

certs = {
    "cafile": args.certificates_path+"/AmazonRootCA1.pem",
    "certfile": args.certificates_path+"/client-cert.pem",
    "keyfile": args.certificates_path+"/private-key.pem",
}

def on_subscribe(mqttc, userdata, mid, granted_qos, properties=None):
    # Publish a plain text payload to topic "sensor01"
    properties = Properties(PacketTypes.PUBLISH)
    properties.UserProperty = [("Content-Type", "text/plain"), ("Hardware-Revision", "brandX-rev1.17c")]
    pub_topic = "sensors/gateway01/sensor01"
    payload = "23.4"
    mqttc.publish(pub_topic, payload, qos=0, properties=properties)
    
    time.sleep(1)
    
    # Publish a base64 encoded payload  to topic "sensor02"
    properties = Properties(PacketTypes.PUBLISH)
    properties.UserProperty = [("Content-Type", "base64"), ("Hardware-Manufacturer", "brandX-rev8.2")]
    pub_topic = "sensors/gateway01/sensor02"
    payload_encoded = base64.b64encode(b"23.7")
    mqttc.publish(pub_topic, payload_encoded, qos=0, properties=properties)
    
    time.sleep(1)
    
    # Publish payload without user properties to topic "sensor03"
    pub_topic = "sensors/gateway01/sensor03"
    payload = "24.4"
    mqttc.publish(pub_topic, payload, qos=0)

def on_connect(mqttc, userdata, flags, reasonCode, properties=None):
    mqttc.subscribe('sensors/gateway01/#', qos=0)

def on_message(mqttc, userdata, message):
    logging.debug(f"Received a message on topic: '{message.topic}'")
    raw_payload = str(message.payload.decode("utf-8"))
    
    if hasattr(message.properties, 'UserProperty'):
        logging.debug(f"Message has user properties: {message.properties.UserProperty}")
        if "Content-Type" in dict(message.properties.UserProperty):
            message_content_type = dict(message.properties.UserProperty)["Content-Type"]
            logging.debug(f"Received message with Content-Type: '{message_content_type}'")
            if message_content_type == "base64":
                decoded_payload = base64.b64decode(raw_payload).decode("utf-8")
                logging.debug(f"Raw payload: '{raw_payload}', Decoded base64 payload: '{decoded_payload}'")
            elif message_content_type == "text/plain":
                logging.debug(f"Plain text payload: '{raw_payload}'")
            else:
                logging.debug(f"Content-Type unknown, raw payload: '{raw_payload}'")
        else:
            logging.debug(f"No Content-Type specified, raw payload: '{raw_payload}'")
    else:
        logging.debug(f"No User Property specified, raw payload: '{raw_payload}'")

mqttc = mqtt.Client("TestThing02", protocol=mqtt.MQTTv5)
logger = logging.getLogger(__name__)
mqttc.enable_logger(logger)
    
mqttc.on_message = on_message
mqttc.on_subscribe = on_subscribe
mqttc.on_connect = on_connect

mqttc.tls_set(certs["cafile"],
                   certfile=certs["certfile"],
                   keyfile=certs["keyfile"],
                   cert_reqs=ssl.CERT_REQUIRED,
                   tls_version=ssl.PROTOCOL_TLSv1_2,
                   ciphers=None)

mqttc.connect(args.endpoint, 8883)
mqttc.loop_forever()