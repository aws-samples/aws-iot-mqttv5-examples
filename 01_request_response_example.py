# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from paho.mqtt.packettypes import PacketTypes
import ssl
import time
from paho.mqtt.properties import Properties
import paho.mqtt.client as mqtt
import logging
import json
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
    # Publish a plain text payload to topic "home07/main_door/lock"
    properties = Properties(PacketTypes.PUBLISH)
    pub_topic = "home07/main_door/lock"

    command_parameters = {
        "user_profile_id": 4,
        "request_id": "eb1bd30a-c7e6-42a4-9e00-d5baee89f65c"
    }

    properties.CorrelationData = json.dumps(command_parameters).encode('utf-8')
    properties.ResponseTopic = "home07/main_door/status"
    payload = "LOCK"
    mqttc.publish(pub_topic, payload, qos=0, properties=properties)
    time.sleep(1)


def on_connect(mqttc, userdata, flags, reasonCode, properties=None):
    mqttc.subscribe('home07/main_door/#', qos=0)


def on_message(mqttc, userdata, message):
    raw_payload = str(message.payload.decode("utf-8"))
    logging.debug(f"Received a message on topic: '{message.topic}', payload: '{raw_payload}'")

    if message.topic == "home07/main_door/lock":
        logging.debug(f"Main door LOCK request with parameters: '{str(message.properties.CorrelationData)}'")
        properties = Properties(PacketTypes.PUBLISH)
        properties.CorrelationData = message.properties.CorrelationData
        response_topic = message.properties.ResponseTopic
        payload = "USER_IS_NOT_AUTHENTICATED"
        mqttc.publish(response_topic, payload, qos=0, properties=properties)
    elif message.topic == "home07/main_door/status":
        logging.debug(f"Main door status: '{raw_payload}'' with parameters: '{str(message.properties.CorrelationData)}'")


mqttc = mqtt.Client("TestThing01", protocol=mqtt.MQTTv5)
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
