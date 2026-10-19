# TempAlerter Type K x4 - MAXI - BETA
# Copyright (C) 2026 Virgil Mehalek
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed WITHOUT ANY WARRANTY; see
# the LICENSE file or <https://www.gnu.org/licenses/> for details.

from machine import Pin


#follow up
#temp sensor types https://www.youtube.com/watch?v=eLe3NAwvfvA

#ds18b20 Temp sensor imports and vars
#import machine, onewire, ds18x20, time

#Inputs: Red (+3 to +5.5v), Black Ground, Yellow Signal to single GPIO pin
#4.7kΩ resistor between the data line and +5V
#is a pull-up resistor, and it serves
#a critical role in the operation of the DS18B20 temperature probe, which
#communicates using the 1-Wire protocol.

import machine, onewire, ds18x20, time

ds_pin = machine.Pin(10)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()
print('Found DS devices: ', len(roms))
print('DS PIN: ', ds_pin)
print()

#----- LOW TEMP PROBE LOOP -----
while True:
    #read the probe(s) and store the temp in registers
    ds_sensor.convert_temp()
    time.sleep(0.75)  # Allow conversion time

    for idx, rom in enumerate(roms, 1):
        #read the temp from the register (not from the probe)
        tempC = ds_sensor.read_temp(rom)
        tempF = tempC * (9/5) + 32
        probe_name = f"TempLow{idx}"
        print(f'{probe_name}: {tempF:.2f}°F  (ROM: {rom.hex()})')

    print()
    time.sleep(1)
        
