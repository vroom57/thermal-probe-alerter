# TempAlerter Type K x2
# Copyright (C) 2026 Virgil Mehalek
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed WITHOUT ANY WARRANTY; see
# the LICENSE file or <https://www.gnu.org/licenses/> for details.

import machine
import time
import onewire, ds18x20

## UNTESTED - written by Gemini
# Stand-alone system check code


# 1. Initialize I2C for LCD1602
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1))

# 2. LED Array
led_pins = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 26]
leds = [machine.Pin(p, machine.Pin.OUT) for p in led_pins]

# 3. Buzzer
buzzer = machine.Pin(27, machine.Pin.OUT)

# 4. DS18B20 Low Temp Probes
ds_pin = machine.Pin(10)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

def test_hardware():
    print("Starting Hardware Diagnostic...")
    
    # Test LEDs sequentially
    for led in leds:
        led.value(1)
        time.sleep(0.1)
        led.value(0)
        
    # Test Buzzer
    buzzer.value(1)
    time.sleep(0.2)
    buzzer.value(0)
    
    # Scan for DS18B20 Probes
    roms = ds_sensor.scan()
    print(f"Found {len(roms)} DS18B20 probes.")
    
    # Read Temps
    ds_sensor.convert_temp()
    time.sleep(0.75)
    for rom in roms:
        temp = ds_sensor.read_temp(rom)
        print(f"Probe {rom.hex()}: {temp:.2f}°C")

# Run test
test_hardware()