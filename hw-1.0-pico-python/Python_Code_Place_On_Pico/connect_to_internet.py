# TempAlerter Type K x2
# Copyright (C) 2026 Virgil Mehalek
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed WITHOUT ANY WARRANTY; see
# the LICENSE file or <https://www.gnu.org/licenses/> for details.

import time
import network
import config

def connect_to_internet(ssid, password):
    # Pass in string arguments for ssid and password
    
    # Just making our internet connection
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
      print ('WLAN=', wlan.status())
      if wlan.status() < 0 or wlan.status() >= 3:
        break
      max_wait -= 1
      print('waiting for connection...')
      time.sleep(1)
    # Handle connection error
    if wlan.status() != 3:
       raise RuntimeError('network connection failed')
    else:
      print('connected')
      status = wlan.ifconfig()
     
# WiFi credentials come from config.py
connect_to_internet(config.WIFI_SSID, config.WIFI_PASSWORD)


# Use Stop/Restart to reconnect.

# Print available networks:
#print(wlan.scan())

# MAC address from WiFi chip OTP
#mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
#print('mac = '+ mac)

# Onboard LED for WiFi: (untested)
# if wlan.status() != 3:
#     raise RuntimeError('Wi-Fi connection failed')
# else:
#     led = machine.Pin('LED', machine.Pin.OUT)
#     for i in range (wlan.status()):
#         led.on()
#         time.sleep(.1)
#         led.off()
#     print('Connected')
#     status = wlan.ifconfig()
#     print('ip = ' + status[0])
