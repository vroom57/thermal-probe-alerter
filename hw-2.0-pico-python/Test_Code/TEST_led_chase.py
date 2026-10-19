# TempAlerter Type K x4 - MAXI - ALPHA
# Copyright (C) 2026 Virgil Mehalek
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed WITHOUT ANY WARRANTY; see
# the LICENSE file or <https://www.gnu.org/licenses/> for details.

from machine import Pin
import time




#myLED=Pin('LED',Pin.OUT) # onboard LED

gpio27_BUZZER=Pin(27,Pin.OUT)


# Top LEDs
gpio11LED_red_LTop=Pin(11,Pin.OUT)
gpio12LED_yel_LTop=Pin(12,Pin.OUT)
gpio13LED_grn_Top=Pin(13,Pin.OUT)
gpio14LED_yel_RTop=Pin(14,Pin.OUT)
gpio15LED_red_RTop=Pin(15,Pin.OUT)

# Right LEDs
gpio16LED_blu_R=Pin(16,Pin.OUT)
gpio17LED_grn_R=Pin(17,Pin.OUT)
gpio18LED_yel_R=Pin(18,Pin.OUT)
gpio19LED_red_R=Pin(19,Pin.OUT)

# Left LEDs
gpio26LED_blu_L=Pin(26,Pin.OUT)
gpio22LED_grn_L=Pin(22,Pin.OUT)
gpio21LED_yel_L=Pin(21,Pin.OUT)
gpio20LED_red_L=Pin(20,Pin.OUT)

### INITIALIZE LEDS and BUZZER
# Top LEDs
gpio11LED_red_LTop.value(0)
gpio12LED_yel_LTop.value(0)
gpio13LED_grn_Top.value(0)
gpio14LED_yel_RTop.value(0)
gpio15LED_red_RTop.value(0)

# Lower Left LEDs
gpio26LED_blu_L.value(0)
gpio22LED_grn_L.value(0)
gpio21LED_yel_L.value(0)
gpio20LED_red_L.value(0)

# Lower Right LEDs
gpio16LED_blu_R.value(0)
gpio17LED_grn_R.value(0)
gpio18LED_yel_R.value(0)
gpio19LED_red_R.value(0)
  
# Buzzer Initialize
gpio27_BUZZER(0)

### Sleep timer to manually set values above and hold
#time.sleep(10000)

while True:

    # Buzzer On
    gpio27_BUZZER.value(1)
    time.sleep(.001)
    gpio27_BUZZER.value(0)


    # Top LEDs
    gpio11LED_red_LTop.value(1)
    time.sleep(.75)
    gpio11LED_red_LTop.value(0)
    gpio12LED_yel_LTop.value(1)
    time.sleep(.75)
    gpio12LED_yel_LTop.value(0)
    gpio13LED_grn_Top.value(1)
    time.sleep(.75)
    gpio13LED_grn_Top.value(0)
    gpio14LED_yel_RTop.value(1)
    time.sleep(.75)
    gpio14LED_yel_RTop.value(0)
    gpio15LED_red_RTop.value(1)
    time.sleep(.75)
    gpio15LED_red_RTop.value(0)


    # Left LEDs
    gpio26LED_blu_L.value(1)
    time.sleep(.75)
    gpio26LED_blu_L.value(0)
    gpio22LED_grn_L.value(1)
    time.sleep(.75)
    gpio22LED_grn_L.value(0)
    gpio21LED_yel_L.value(1)
    time.sleep(.75)
    gpio21LED_yel_L.value(0)
    gpio20LED_red_L.value(1)
    time.sleep(.75)
    gpio20LED_red_L.value(0)
   

    # Right LEDs
    gpio16LED_blu_R.value(1)
    time.sleep(.75)
    gpio16LED_blu_R.value(0)
    gpio17LED_grn_R.value(1)
    time.sleep(.75)
    gpio17LED_grn_R.value(0)
    gpio18LED_yel_R.value(1)
    time.sleep(.75)
    gpio18LED_yel_R.value(0)
    gpio19LED_red_R.value(1)
    time.sleep(.75)
    gpio19LED_red_R.value(0)
    




