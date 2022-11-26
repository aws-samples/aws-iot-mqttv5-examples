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

parser = argparse.ArgumentParser()
parser.add_argument('--endpoint', dest='endpoint', type=str, required=True, help='Obtain your Device data endpoint for your AWS Account')
parser.add_argument('--certificates-path', dest='certificates_path', default='certificates', 
                    type=str, required=False, help='Modify the cert folder path if your certificates are in another folder')

args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG)

certs = {
    "cafile": args.certificates_path+"/AmazonRootCA1.pem",
    "certfile": args.certificates_path+"/client-cert.pem",
    "keyfile": args.certificates_path+"/private-key.pem",
}


def on_connect(mqttc, user_data, flags, reason_code, properties=None):
    logging.debug(f"Connected {flags}")
    
    # Publishing 1 message without a topic alias
    topic = "sensors/field/field001/equipments/9e6282ff-c8f0-49cd-b3a0-fa17ad6b84a7/temperature"
    payload = "23.4"
    mqttc.publish(topic, payload, qos=1)
    
    time.sleep(1)
    
    # Publishing 1 message with a topic alias
    properties = Properties(PacketTypes.PUBLISH)
    properties.TopicAlias = 14
    topic = "sensors/field/field001/equipments/46be210d-8a83-4e92-a3fe-4f989704d21e/temperature"
    payload = "26.2"
    mqttc.publish(topic, payload, qos=1, properties=properties)
    
    
def on_disconnect(mqttc, user_data, reason_code, properties=None):
    logging.debug(f"Received Disconnect with reason: {reason_code}")
    if reason_code == 148:
        logging.debug(
            "The disconnect is caused by the topic alias. Logging the issue for further analysis and exiting.")
        exit()
    else:
        logging.debug(
            "The disconnect reason doesn't have a specific action to take.")
    
def on_publish(client,userdata, result,properties=None):
    logging.debug(f"Published {result}")

mqttc = mqtt.Client("TestThing05", protocol=mqtt.MQTTv5)
logger = logging.getLogger(__name__)
mqttc.enable_logger(logger)

mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect

mqttc.tls_set(certs["cafile"],
                   certfile=certs["certfile"],
                   keyfile=certs["keyfile"],
                   cert_reqs=ssl.CERT_REQUIRED,
                   tls_version=ssl.PROTOCOL_TLSv1_2,
                   ciphers=None)

mqttc.connect(args.endpoint, 8883)

mqttc.loop_forever()

