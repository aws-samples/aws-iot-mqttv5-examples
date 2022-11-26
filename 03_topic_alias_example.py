# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from paho.mqtt.packettypes import PacketTypes
import ssl
import time
from paho.mqtt.properties import Properties
import paho.mqtt.client as mqtt
import logging
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

mqttc = mqtt.Client("TestThing03", protocol=mqtt.MQTTv5)
logger = logging.getLogger(__name__)
mqttc.enable_logger(logger)


mqttc.tls_set(certs["cafile"],
              certfile=certs["certfile"],
              keyfile=certs["keyfile"],
              cert_reqs=ssl.CERT_REQUIRED,
              tls_version=ssl.PROTOCOL_TLSv1_2,
              ciphers=None)

mqttc.connect(args.endpoint, 8883)

properties = Properties(PacketTypes.PUBLISH)
properties.TopicAlias = 1

topic = "sensors/field/field001/equipments/a804e598-ee90-4f89-9cde-458f8fe9b980/temperature"

payload = "23.4"
mqttc.publish(topic, payload, qos=0, properties=properties)

time.sleep(1)

payload = "25.5"
mqttc.publish('', payload, qos=0, properties=properties)

time.sleep(1)

payload = "22.2"
mqttc.publish('', payload, qos=0, properties=properties)
