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
parser.add_argument('--session-expiry-interval', dest='session_expiry_interval', type=int, 
                    required=True, help='Set MQTT session expiry interval value in seconds')

args = parser.parse_args()

certs = {
    "cafile": args.certificates_path+"/AmazonRootCA1.pem",
    "certfile": args.certificates_path+"/client-cert.pem",
    "keyfile": args.certificates_path+"/private-key.pem",
}

def sub_client_on_connect(mqtt_sub, user_data, flags, reason_code, properties=None):
    mqtt_sub.subscribe('vehicle/#', qos=1)
    time.sleep(1)

def sub_client_on_message(mqtt_sub, user_data, message):
    raw_payload = str(message.payload.decode("utf-8"))
    logging.debug(f"Received a message on topic: '{message.topic}', payload: '{raw_payload}'")


# Subscriber client
mqtt_sub = mqtt.Client("TestThing04-Sub", protocol=mqtt.MQTTv5)
logger = logging.getLogger(__name__)
mqtt_sub.enable_logger(logger)
    
mqtt_sub.on_message = sub_client_on_message
mqtt_sub.on_connect = sub_client_on_connect

mqtt_sub.tls_set(certs["cafile"],
                   certfile=certs["certfile"],
                   keyfile=certs["keyfile"],
                   cert_reqs=ssl.CERT_REQUIRED,
                   tls_version=ssl.PROTOCOL_TLSv1_2,
                   ciphers=None)

# Connect to sub client
properties_connect = Properties(PacketTypes.CONNECT)
properties_connect.SessionExpiryInterval = args.session_expiry_interval
mqtt_sub.connect(args.endpoint, 8883, clean_start=False, properties=properties_connect)

mqtt_sub.loop_forever()