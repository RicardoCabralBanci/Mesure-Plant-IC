#-*- coding: utf-8 -*-

#System Stuff
import time
import ssl
#Libs
import paho.mqtt.client as mqttClient

#This class handles MQTT connections
class mqtt_connection:
    def __init__(self, client_id, address, port, usr, pwd, topic, on_message, cert=None):
        self.Connected = False                  #global variable for the state of the connection

        self.broker_address= address            #Broker address
        self.port = port                        #Broker port
        self.user = usr                         #Connection username
        self.password = pwd                     #Connection password
        self.client_id = client_id              #Client id
        self.topic = topic                      #Topic
        self.on_message = on_message
        self.client = mqttClient.Client(self.client_id)                     #create new instance
        self.client.username_pw_set(self.user, password=self.password)      #set username and password
        self.client.on_connect= self._on_connect                            #attach function to connection established call
        self.client.on_disconnect= self._on_disconnect                      #attach function to connection lost call
        self.client.on_message= on_message                                  #attach function to callback
        if cert is not None:					                            #attach tls if given a certificate
            self.client.tls_set(cert, tls_version=ssl.PROTOCOL_TLSv1_2)
        self.client.connect(self.broker_address, port=self.port)          #connect to broker
        self.client.loop_start()                                          #start the loop

        while self.Connected != True:    #Wait for connection
            time.sleep(0.1)
    
    def publish_to_topic(self,msg):
        if self.Connected:
            self.client.publish(self.topic,msg)
        else:
            print('client is not connected')

    def _on_disconnect(self, client, userdata, rc):
        self.Connected = False
        if rc != 0:
                print ("Unexpected MQTT disconnection. Attempting to reconnect.")
                self.Connected = False
                        
    def _on_connect(self, client, userdata, flags, r):
        if r == 0:
            print(self.client_id + " Connected to broker")
            self.Connected = True
            self.client.subscribe(self.topic)
        else:
            print("Connection failed")
    
    def clean_up(self):
        self.client.disconnect()
        self.client.loop_stop()
