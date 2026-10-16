# TempAlerter Type K x2
# Copyright (C) 2026 Virgil Mehalek
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed WITHOUT ANY WARRANTY; see
# the LICENSE file or <https://www.gnu.org/licenses/> for details.

from machine import Pin


# Follow up
# Temp sensor types https://www.youtube.com/watch?v=eLe3NAwvfvA

# DS18B20 temp sensor imports and vars
#import machine, onewire, ds18x20, time

# Inputs: Red (+3 to +5.5V), Black Ground, Yellow Signal to single GPIO pin
# 4.7kΩ resistor between the data line and +5V
# is a pull-up resistor, and it serves
# a critical role in the operation of the DS18B20 temperature probe, which
# communicates using the 1-Wire protocol.

import machine, onewire, ds18x20
ds_pin = machine.Pin(10)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()
#print('Found DS devices: ', roms)
#print('DS PIN: ', ds_pin)

# Read the probe(s) and store the temp in registers
ds_sensor.convert_temp()

#----- LOW TEMP PROBE -----
for rom in roms:
    #print(rom)
    # Read the temp from the register (not from the probe)
    tempC = ds_sensor.read_temp(rom)
    tempF = tempC * (9/5) +32
    #print('temperature (ºC):', "{:.2f}".format(tempC))
    print('Low-TEMP: temperature (ºF):', "{:.2f}".format(tempF))
    print()
        
