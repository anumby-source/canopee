#!/usr/bin/env python3
import os
import paho.mqtt.client as mqtt #import the client1
import time

############
def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    monMes = str(message.payload.decode("utf-8"))
    print("message topic=",message.topic)
    if monMes == "Bon":
        os.system('aplay -D bluealsa:DEV=08:DF:1F:87:AF:26 /home/pi/Music/applause6.wav')
    else:
        os.system('aplay -D bluealsa:DEV=08:DF:1F:87:AF:26 /home/pi/Music/Crackling_Fireplace.wav')
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
#############
broker_address="192.168.1.100"
#broker_address="iot.eclipse.org"
print("creating new instance")
client = mqtt.Client("can1")   # create new instance
client.on_message=on_message   # attach function to callback
print("connecting to broker")
client.connect(broker_address) # connect to broker
client.loop_start()            # start the loop
print("Subscribing to topic","Canopee/etat")
client.subscribe("Canopee/etat")
time.sleep(4)                  # wait
client.loop_forever()

