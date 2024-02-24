#!/usr/bin/env python3
#http server for https://github.com/cyakimov/homebridge-http-contact-sensor
#reading the tasmota energy meter plug to device weither the tumble dryier is done or not
#https://github.com/yjeanrenaud/yj_appliance4homebridge
# Make you old home appliance smart home ready!
# This small python script is turning an old tumble dryer or any other old home appliance *smart* by hooking it up to [homebridge](https://github.com/homebridge/homebridge) so it can be used in Apple HomeKit and Google Home Assistant (via [homebridge-gsh](https://github.com/oznu/homebridge-gsh)https://github.com/oznu/homebridge-gsh) alike.
# In fact I have a some years old [Beko DE8635RX](https://www.beko.com/de-de/produkte/trockner/trockner-w%C3%A4rmepumpentrockner-8-kg-de8635rx) that is not smart, which is good. But when the machine is done with tumbling my clothes, it keeps itsself in a somewhat standby that consumes about 11 Watt of energy, which I dislike. so I wrote this small script to get notified when the machine is doing that and I can go into the basement, take out the clothes and turn that thing off. Yes, I am somewhat lazy.
#
#Yves Jeanrenaud, 2024

import requests
import time 
import datetime
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
#from http.server import SimpleHTTPRequestHandler
import threading

# we need basename to know what this script file is called like
from os.path import basename
import os
tasmota_hostname ="192.168.1.11" #the name (or IP-address) of your Tasmota energy meter
#setup the variables for the http-server
is_standby = 0 # 1 means it is done or off
is_running = 0 # 1 means it is running
version='0.0.2'
port=8099

#golbal vars to store read values
global power
global current
global countdown

global check_delay
check_delay = 10 #seconds between two pollings
#set the limits for deciding if we are looking at a standby device
power_min = 1
power_max = 12
#between 1 and 12 W means: we are in standby

def get_values_from_tasmota():
    global power
    global current
    try:
        response = requests.get("http://"+str(tasmota_hostname)+"/cm?cmnd=status%208")
        data = response.json()
    except:
        print("tasmota not online")
        exit(0)
    
    #print(type(data))
    #print(data['StatusSNS']['ENERGY']['Power'])
    power = data['StatusSNS']['ENERGY']['Power']
    # power is about 71-80 while TV is on, blank screen is about 60, in standby it is about 14 W
    # current is about 0.34-0.37 while TV is on, blank screen 0.298, about 0.119 in standby
    current = data['StatusSNS']['ENERGY']['Current']
    #print(type (power))
    #print(type (current))
    print ("power is {:2d} W".format(power)+" at " +str(datetime.datetime.now()))

def check_tumbledryer_thread(): ##function for the second thread
   while 1:
      get_values_from_tasmota()
      global is_standby
      global is_running
      #print ('power is '+str(power))
      if power > power_min and power < power_max:
         is_standby = 1
      else:
         is_standby = 0 
      print('is_standby = ' + str(is_standby))
      if power > 0:
        is_running = 1
      else:
        is_running = 0
      print('is_running = ' + str(is_running))
      #pause
      time.sleep(check_delay) #and yes, we can keep the thread busy and don't care for drift
   #end of endless while
#end of check_tumbledryer_thread


class server_handler(BaseHTTPRequestHandler):

   def _set_headers(self):
      #overwrite server info string. Only works for BaseHTTPRequestHandler, not SimpleHTTPRequestHandler
      self.server_version=str(basename(__file__))+'/'+version
      #'yj_watch_trockner.py/0.0.2'
      self.sys_version=''
      self.send_response(200)
      self.send_header('Content-type', 'text/html; charset=utf-8')
      self.end_headers()
        
   def do_HEAD(self):
      self._set_headers()
      
   # GET sends back a message
   def do_GET(self):
      self._set_headers()
      if self.path != '/' and self.path != '/is_running' and self.path != '/is_standby' and self.path != '/watt' and self.path != '/is_running/' and self.path != '/is_standby/' and self.path != '/watt/':
         self.send_error(404, "Object not found")
         return
      #check_router_thread()
      #self.wfile.write(bytes("<html><body><h1>"+str(is_standby)+"</h1></body></html>",'utf-8')) #debug
      #self.wfile.write(is_standby.to_bytes(2,'big'))
      elif self.path == '/' or self.path == '/is_standby' or self.path == '/is_standby/':
         self.wfile.write(bytes(str(is_standby),'utf-8'))
         return
      elif self.path == '/is_running' or self.path == '/is_running/':
         self.wfile.write(bytes(str(is_running),'utf-8'))
         return
      elif self.path == '/watt' or self.path == '/watt/':
         self.wfile.write(bytes(str(power),'utf-8'))
         return
      self.wfile.write(bytes(str(is_standby),'utf-8'))
   
   def do_POST(self):
      # refuse to receive any content
      self.send_response(400)
      self.end_headers()
      return
   
   def log_message(self, format, *args):
      return #to silent the log messages
#end class server_handler

class server_thread(threading.Thread):#oop ftw

   def __init__(self,port):
      threading.Thread.__init__(self)
      self.port = port
      self.daemon = True
      self.start()
      #print(self)
      
   def run(self):
      server_address = ('', self.port)
      server_version=str(basename(__file__))+'/'+version
      httpd = HTTPServer(server_address, server_handler)
      print ('starting httpd on port %d...' % self.port)
      httpd.serve_forever()
   #end of run
#end of server_thread

if __name__ == "__main__":
    server_thread(port)
    th2 = threading.Thread(target=check_tumbledryer_thread,daemon=True)
    th2.start()
    while(1):
        time.sleep(1) # to keep the script running
#eof
