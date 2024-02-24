# yj_appliance4homebridge
Make you old home appliance smart home ready!
This small python script is turning an old tumble dryer or any other old home appliance *smart* by hooking it up to [homebridge](https://github.com/homebridge/homebridge) so it can be used in Apple HomeKit and Google Home Assistant (via [homebridge-gsh](https://github.com/oznu/homebridge-gsh)https://github.com/oznu/homebridge-gsh) alike.

In fact I have a some years old [Beko DE8635RX](https://www.beko.com/de-de/produkte/trockner/trockner-w%C3%A4rmepumpentrockner-8-kg-de8635rx) that is not smart, which is good. But when the machine is done with tumbling my clothes, it keeps itsself in a somewhat standby that consumes about 11 Watt of energy, which I dislike. so I wrote this small script to get notified when the machine is doing that and I can go into the basement, take out the clothes and turn that thing off. Yes, I am somewhat lazy.

# Prerequisites
- This programme relies on python 3. No special modules needed.
- It relies on a [Tasmotasmart meter](https://www.pocketpc.ch/magazin/testberichte/smart-home/review-refoss-smarte-wlan-steckdosenadapter-mit-tasmota-firmware-im-test-91562/) to read the power consumption.
- the scripts needs to run permanently, so I hooked it up on a [Raspberry Pi 3B+](https://www.raspberrypi.com/products/raspberry-pi-3-model-b-plus/) which I use for various other tasks in my home already. (for instance, it hosts the [homebridge](https://github.com/homebridge/homebridge) installation, too)

# Setup
The setup is easy. You configure the [Tasmota smart meter](https://www.pocketpc.ch/magazin/testberichte/smart-home/review-refoss-smarte-wlan-steckdosenadapter-mit-tasmota-firmware-im-test-91562/) to a fixed IP address and enable its HTTP API. This is afaik enabled by default, but you may find the settiungs under *Configuration*, *Configure Other* where you may just check the box for *HTTP API enable* and hit *Save*.
Then, the python script needs three values (`tasmota_hostname`, `power_min` and `power_max`) from you:
- on line 22: `tasmota_hostname ="192.168.1.11" ` you obviously enter the IP-Address of your Tasmotaenergy meter in place (or the hostname if you're fancy avahi/bonjour)
- on line 36: `power_min = 1` is the lower limit
- on line 37: `power_max = 12` that's the upper limit. These two values specify when we consider the appliance to be in a standby mode. For the named Beko DE8635RX that is about 11 Watt.
- *(optional)* on line 27: `port = 8099` may be configured to any port available at your machine.
- *(optional)* on line 35:  `check_delay = 10` where you configure the amount of seconds between two readings of the energy meter. I figured 10 seconds is fair enough
- install and configure [homebridge](https://github.com/homebridge/homebridge) 
# Usage
Just run the script py `python3 yj_appliance4homebridge.py` or, if you wish `chmod a+x yj_appliance4homebridge.py` and then `./yj_appliance4homebridge`. You will see the current power read from the Tasmota energy meter and the values for the two variables  *is_standby* and *is_running*. These are exposed as HTTP messages under:
[http://[IP]:[Port]/is_running](http://[IP]:[Port]/is_running) and [http://[IP]:[Port]/is_standby](http://[IP]:[Port]/is_standby)
You may also use cron to run it automatically at system start in a `screen` (install screen first via `sudo apt-get update && sudo apt-get install screen`
`$crontab -e`
and insert the following line at the end:
`@reboot screen -dmS yjhbitumbledryer python3 /FULL/PATH/TO/SCRIPT/yj_appliance4homebridge.py`

# Apple HomeKit / Smart Home integration
If you want to use this in your Apple HomeKit smart home, use [homebridge](https://www.homebridge.org) and the [homebridge-http-contact-sensor plugin](https://github.com/cyakimov/homebridge-http-contact-sensor).
There, the config should look somehwat like this
```
{
    "accessory": "ContactSensor",
    "name": "Tumblydryer running",
    "pollInterval": 60000,
    "_comment_": "1 min in milliseonds",
    "statusUrl": "http://192.168.1.3:8099/is_running"
},
{
    "accessory": "ContactSensor",
    "name": "Tumblydryer standby",
    "pollInterval": 60000,
    "_comment_": "1 min in milliseonds",
    "statusUrl": "http://192.168.1.3:8099/is_standby"
},
```
where the `status-url` obiously contains the *IP address* (or the hostname) of the machine running this script and the *port* you speficied. These URL's just print out a blunt *0* if false and *1* if true.
That's it! you restart homebridge and it's registered now as two contact sensosr within HomeKit thereafter.

Therefore, you may use this to alert you on your iOS device when your applicance is in stanbdy and when it is actually working via HomeKit. Of course, you may use these new contact sensors now also for other automatisations. It also works with Google HomeKit and other smart home apps, obviously. You 
# Todos
- clean up the code
