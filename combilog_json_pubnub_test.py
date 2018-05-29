#!/usr/bin/env python3
#
# Circutor CVM-1D test
#
import time
import os
import requests
from pymodbus.constants import Endian
from pymodbus.constants import Defaults
Defaults.Reconnects = 15
Defaults.RetryOnEmpty = True
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
 
pnconfig = PNConfiguration()
 
pnconfig.subscribe_key = 'sub-c-d68e7eae-39d8-11e6-b006-02ee2ddab7fe'
pnconfig.publish_key = 'pub-c-b1e82969-2014-4b85-9d30-90c95f74df18'
 
pubnub = PubNub(pnconfig)
 
 
def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];
 
 
class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass  # handle incoming presence data
 
    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost
 
        elif status.category == PNStatusCategory.PNConnectedCategory:
            pass
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            # pubnub.publish().channel("testeon").message("hello!!").async(my_publish_callback)
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass
            # Handle message decryption error. Probably client configured to
            # encrypt messages and on live data feed it received plain text.
 
    def message(self, pubnub, message):
        print(message.message)  # Handle new message stored in message.message

testinet = False
while (testinet == False):
    time.sleep(1)
    try:
        pubnub.add_listener(MySubscribeCallback())
        pubnub.subscribe().channels('testeon').execute()
        testinet = True
    except:
        testinet = False
print("Pubnub connected")
        
testmodbus = False
while (testmodbus == False):
    client = ModbusClient(method='rtu', port='/dev/serial/by-id/usb-FTDI_USB-RS485_Cable_FTZ1SY80-if00-port0', timeout=10, stopbits = 1, bytesize = 8,  parity='N', baudrate= 19200)
    testmodbus = client.connect()
    time.sleep(1)
print("Modbus connected")

while True:
    while True:
        try:
            rr1 = client.read_input_registers(address=0, count=2, unit=1)
            decoder1 = BinaryPayloadDecoder.fromRegisters(rr1.registers, endian=Endian.Big)
            t=decoder1.decode_32bit_uint()/10
            break
        except AttributeError:
            print("Modbus Error")
            time.sleep(1)
            
    strmessage={"eon":{"Temperature": t,"Humidity": 0,"CMP10": 0,"PQS1": 0,"Precipitation": 0}}
    pubnub.publish().channel("testeon").message(strmessage).async(my_publish_callback)
    
    API_WEERSTATION = "https://energieberekeningen.com/api/weerstation"
    API_KEY = "RPI_2018"
    
    # data to be sent to api
    data = {
        'API_KEY': API_KEY,
        'temperatuur': t,
        'vochtigheid': 0,
        'pluviometer': 0,
        'pyranometer': 0,
        'PAR' : 0
    }
 
    # sending post request and saving response as response object
    r = requests.post(url = API_WEERSTATION, data = data)
 
    # extracting response text 
    pastebin_url = r.text
    print("The pastebin URL is:%s"%pastebin_url)   
    
    time.sleep(10)