#! /bin/sh
/usr/bin/aplay -D bluealsa:DEV=08:DF:1F:87:AF:26 /home/pi/Music/applause6.wav
mosquitto_pub -h localhost -t canopee/etat -m Bon
