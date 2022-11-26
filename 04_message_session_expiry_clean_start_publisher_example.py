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

def pub_client_on_connect(mqtt_sub, user_data, flags, reason_code, properties=None):
    properties=Properties(PacketTypes.PUBLISH)
    properties.MessageExpiryInterval = 10
    payload = "UNLOCK"
    topic = "vehicle/driver_door/lock"
    mqtt_pub.publish(topic, payload, qos=1, properties=properties)
    
    time.sleep(1)
    
    properties.MessageExpiryInterval = 120
    payload = "PRE_HEAT"
    topic = "vehicle/air_conditioner/set"
    mqtt_pub.publish(topic, payload, qos=1, properties=properties)


# Publisher client
mqtt_pub = mqtt.Client("TestThing04-Pub", protocol=mqtt.MQTTv5)
logger = logging.getLogger(__name__)
mqtt_pub.enable_logger(logger)

mqtt_pub.on_connect = pub_client_on_connect

mqtt_pub.tls_set(certs["cafile"],
                   certfile=certs["certfile"],
                   keyfile=certs["keyfile"],
                   cert_reqs=ssl.CERT_REQUIRED,
                   tls_version=ssl.PROTOCOL_TLSv1_2,
                   ciphers=None)

mqtt_pub.connect(args.endpoint, 8883)
mqtt_pub.loop_forever()