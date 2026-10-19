# TempAlerter Type K x4 - MAXI - ALPHA
# Copyright (C) 2026 Virgil Mehalek
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed WITHOUT ANY WARRANTY; see
# the LICENSE file or <https://www.gnu.org/licenses/> for details.

# ******************* DISCLAIMER *******************
# This is a personal hobby project, provided "as is" without warranty of any
# kind. Use it at your own risk.
#
# It is NOT designed, tested, or certified for life-safety, fire-protection,
# medical, or other critical uses, and must not be relied on to protect
# people, animals, or property. Temperature readings may be inaccurate, and
# alerts (LEDs, display, and email) can be delayed or fail entirely because
# of sensor, wiring, WiFi, power, or software faults.
#
# Always use properly certified safety devices (smoke and CO detectors,
# thermal cutoffs, etc.) for anything that matters. The author accepts no
# liability for any damage, injury, or loss resulting from use of this code
# or hardware design.
# **************************************************

from machine import I2C, Pin, WDT
import time
from max6675 import MAX6675
import network
import connect_to_internet  #via wifi (credentials in config.py)
import umail
import config
from lcd_pico_i2c import I2cLcd
import machine, onewire, ds18x20
from wifi_ping import icmp_ping

#import utime

# ******************* CONSTANTS ********************

EMAIL_ENABLED = False  # Set to False to disable email notifications for testing
resend_email_interval = 120  # Time in seconds between resend attempts while condition persists
WATCHDOG_ENABLED = False  # Set to False to disable watchdog during troubleshooting
TEST_WATCHDOG = False  # Set to True to test watchdog auto-reboot
MAX_TEMP_WINDOW = 1200  # Time window in seconds to track max temperature (resets after this duration)
SOUND_ENABLED = True  # Set to False to disable buzzer/sound alerts
BEEP_DURATION = 0.1  # Beep duration in seconds (configurable)
KEEPALIVE_ENABLED = False  # Set to False to disable WiFi keepalive pings
KEEPALIVE_INTERVAL = 45  # Seconds between keepalive pings (enables ASUS mesh roaming)

# Internal email state tracking
already_sent = 1  # 1 = email not sent yet, 0 = primed to send


# ******************* WIFI KEEPALIVE FUNCTION ********************
def wifi_keepalive_icmp_ping():
    """Send ICMP echo requests to gateway to force WiFi activity and enable mesh roaming"""
    try:
        gateway = wlan.ifconfig()[2]  # Extract gateway from (IP, netmask, gateway, DNS)
        sent, received = icmp_ping(gateway, count=3, timeout=2000)
        if received > 0:
            print(f"[KEEPALIVE] ICMP ping successful to gateway {gateway} ({received}/{sent} replies)")
            return True
        else:
            print(f"[KEEPALIVE] ICMP ping failed to gateway {gateway} (no responses)")
            return False
    except Exception as e:
        print(f"[KEEPALIVE] ICMP ping error: {e}")
        return False


# ****************   Temp Range Values
# Example Blue < 192, Green < 192 to 230, Yellow 230 - 245 High > 250
# Org Values
#under_val = 192
#low_val = 234
#high_val = 247

# Updated Values
#under_val = 180
#low_val = 227
#high_val = 235

#Test values for room temp
under_val = 76
low_val = 82
high_val = 85


temp_calibration_TempK_1_RightIn = 0    #TK1RIn
temp_calibration_TempK_2_LeftIn = 0     #TK2LIn
temp_calibration_TempK_3_RightOut = 0   #TK3ROut
temp_calibration_TempK_4_LeftOut = -10  #TK4LOut

# Low temp probe calibration
temp_calibration_low1 = 0
temp_calibration_low2 = 0
temp_calibration_low3 = 0
temp_calibration_low4 = 0


####################### DEFINITIONS ###################


# *********** Setup 20x4 Display *********
# Initialize the I2C bus (this can get moved up if the i2c bus is being used for other things too)
# I2C0 Specify the SCL and SDA pins
scl_pin0 = Pin(1)  # Replace with the actual SCL pin number on your Pico
sda_pin0 = Pin(0)  # Replace with the actual SDA pin number on your Pico
i2c0 = I2C(0, scl=scl_pin0, sda=sda_pin0, freq=400000)

I2C_DISP_ADDR = 39
lcd = I2cLcd(i2c0, I2C_DISP_ADDR, 4, 20)

#LCD display’s cursor to flash (blink) on and off,
#lcd.blink_cursor_on()

lcd.backlight_on()
lcd.clear()  #clear hear since display gets filled and I don't like the refresh look

#inumierate i2c 0 bus for troubleshooting
#I2C_ADDR = i2c0.scan()[0]  #first item only, if multipes you will need to inumerate diffrently
#print("I2C0 Bus Items: ",I2C_ADDR)


lcd.putstr("booting....") 


# *********** Initilaize LED Variables ***********
# Onbard LED (not used since covered)
#myLED=Pin('LED',Pin.OUT)

# Top LED's
gpio_LED_Blu_Top=Pin(12,Pin.OUT)
gpio_LED_Blu_Top.value(0)
gpio_LED_Grn_Top=Pin(13,Pin.OUT)
gpio_LED_Grn_Top.value(0)
gpio_LED_Yel_Top=Pin(14,Pin.OUT)
gpio_LED_Yel_Top.value(0)
gpio_LED_Red_Top=Pin(15,Pin.OUT)
gpio_LED_Red_Top.value(0)


# Left Lower LED's
gpio_LED_Blu_L=Pin(26,Pin.OUT)
gpio_LED_Blu_L.value(0)
gpio_LED_Grn_L=Pin(22,Pin.OUT)
gpio_LED_Grn_L.value(0)
gpio_LED_Yel_L=Pin(21,Pin.OUT)
gpio_LED_Yel_L.value(0)
gpio_LED_Red_L=Pin(20,Pin.OUT)
gpio_LED_Red_L.value(0)

# Right Lower LED's
gpio_LED_Blu_R=Pin(16,Pin.OUT)
gpio_LED_Blu_R.value(0)
gpio_LED_Grn_R=Pin(17,Pin.OUT)
gpio_LED_Grn_R.value(0)
gpio_LED_Yel_R=Pin(18,Pin.OUT)
gpio_LED_Yel_R.value(0)
gpio_LED_Red_R=Pin(19,Pin.OUT)
gpio_LED_Red_R.value(0)

# *********** Initialize Buzzer ***********
gpio_buzzer = Pin(27, Pin.OUT)  #GP27 - Buzzer via 2N2222 transistor
gpio_buzzer.value(0)

def beep(duration=BEEP_DURATION):
    """Sound buzzer for specified duration (in seconds) if SOUND_ENABLED"""
    if SOUND_ENABLED:
        gpio_buzzer.value(1)
        time.sleep(duration)
        gpio_buzzer.value(0)




# *********** Set up network DHCP ***********
gpio_LED_Grn_Top.value(0)
wlan = network.WLAN(network.STA_IF)
print("\n[BOOT] WiFi Connection Attempt")
attempt = 0
while wlan.status() != 3 and attempt < 15:
    attempt += 1
    print(f"  Attempt {attempt}/10...", end="")
    time.sleep(1)
    print(f" Status: {wlan.status()}")

ip_address = wlan.ifconfig()[0]
print("\n[BOOT] WiFi Status")
print(f"  IP Address: {ip_address}")
if wlan.status() == 3:
    gpio_LED_Grn_Top.value(1)
    signal_strength = wlan.status('rssi')
    print(f"  Status: CONNECTED (RSSI: {signal_strength} dBm)")
else:
    gpio_LED_Red_Top.value(0)
    print("  Status: OFFLINE")




# *********** Initialize Temp Sensors ***********
# Shared SPI bus for all MAX6675 sensors
sck_shared = Pin(2, Pin.OUT)
so_shared = Pin(4, Pin.IN)

# High temp sensor code - 4 probes on shared SPI bus
# Each sensor has its own CS pin
hi_sensor_TempK_1_RightIn = MAX6675(Pin(6, Pin.OUT), sck_shared, so_shared)  #TK1RIn
hi_sensor_TempK_2_LeftIn = MAX6675(Pin(3, Pin.OUT), sck_shared, so_shared)   #TK2LIn
hi_sensor_TempK_3_RightOut = MAX6675(Pin(8, Pin.OUT), sck_shared, so_shared) #TK3ROut
hi_sensor_TempK_4_LeftOut = MAX6675(Pin(9, Pin.OUT), sck_shared, so_shared)  #TK4LOut

# Low temp sensor code - DS18B20 probes on 1-Wire bus (GP10)
ds_pin = machine.Pin(10)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
low_roms = ds_sensor.scan()
print(f"\n[BOOT] Sensors Initialized")
print(f"  High-Temp Probes (MAX6675): 4 on shared SPI bus")
print(f"  Low-Temp Probes (DS18B20): {len(low_roms)} on 1-Wire bus")

#Stabilization loop, sometimes the first readings from the probes are off
#This allows better readings
print("\n[BOOT] Stabilizing Sensor Readings (3 iterations)...")
counter = 0
while counter < 3:
    counter += 1
    print(f"  Iteration {counter}:")

    #----- HIGH TEMP PROBES -----
    cel_temp = (hi_sensor_TempK_1_RightIn.read())
    fer_temp_TempK_1_RightIn = (cel_temp * 1.8) + 32
    cel_temp = (hi_sensor_TempK_2_LeftIn.read())
    fer_temp_TempK_2_LeftIn = (cel_temp * 1.8) + 32
    cel_temp = (hi_sensor_TempK_3_RightOut.read())
    fer_temp_TempK_3_RightOut = (cel_temp * 1.8) + 32
    cel_temp = (hi_sensor_TempK_4_LeftOut.read())
    fer_temp_TempK_4_LeftOut = (cel_temp * 1.8) + 32
    print(f"    HighTemp: 1={fer_temp_TempK_1_RightIn:.1f}°F 2={fer_temp_TempK_2_LeftIn:.1f}°F 3={fer_temp_TempK_3_RightOut:.1f}°F 4={fer_temp_TempK_4_LeftOut:.1f}°F")

    #----- LOW TEMP PROBES -----
    ds_sensor.convert_temp()
    time.sleep(0.75)
    low_temps = []
    for idx, rom in enumerate(low_roms, 1):
        cel_temp = ds_sensor.read_temp(rom)
        fer_temp_low = (cel_temp * 1.8) + 32
        low_temps.append(f"L{idx}={fer_temp_low:.1f}°F")
    print(f"    LowTemp:  {' '.join(low_temps)}")

    time.sleep(1)


start_time = time.time()  # Initialize start time entering the loop
trigger_flag = 0  # Variable to set after 2 minutes

# Initialize max temperature tracking (rolling window)
max_temp_TempK_1_RightIn = 0
max_temp_reset_time_TempK_1_RightIn = time.time()
max_temp_TempK_2_LeftIn = 0
max_temp_reset_time_TempK_2_LeftIn = time.time()
max_temp_TempK_3_RightOut = 0
max_temp_reset_time_TempK_3_RightOut = time.time()
max_temp_TempK_4_LeftOut = 0
max_temp_reset_time_TempK_4_LeftOut = time.time()

# Initialize overtemp event tracking (independent from rolling max)
overtemp_flag_TempK_1_RightIn = False
overtemp_max_TempK_1_RightIn = 0
overtemp_start_time_TempK_1_RightIn = 0

overtemp_flag_TempK_2_LeftIn = False
overtemp_max_TempK_2_LeftIn = 0
overtemp_start_time_TempK_2_LeftIn = 0

overtemp_flag_TempK_3_RightOut = False
overtemp_max_TempK_3_RightOut = 0
overtemp_start_time_TempK_3_RightOut = 0

overtemp_flag_TempK_4_LeftOut = False
overtemp_max_TempK_4_LeftOut = 0
overtemp_start_time_TempK_4_LeftOut = 0

# Buzzer state tracking for TempK_1_RightIn and TempK_2_LeftIn
previous_status_TempK_1_RightIn = "under"
transition_beep_TempK_1_RightIn = False

previous_status_TempK_2_LeftIn = "under"
transition_beep_TempK_2_LeftIn = False

# Initialize watchdog timer
if WATCHDOG_ENABLED:
    watchdog = WDT(timeout=8000)  # 8000ms = 8 seconds (max is 8388ms)
    print("\n[BOOT] Watchdog Timer: ENABLED (8s timeout)")
else:
    watchdog = None
    print("\n[BOOT] Watchdog Timer: DISABLED")

# Initialize WiFi keepalive tracking
last_ping_time = time.time()
if KEEPALIVE_ENABLED:
    print(f"\n[BOOT] WiFi Keepalive (ICMP ping): ENABLED ({KEEPALIVE_INTERVAL}s interval, 3 pings per check)")
else:
    print("\n[BOOT] WiFi Keepalive (ICMP ping): DISABLED")

############################# DO THE WORK ########################
while True:

    # WiFi heartbeat
    if wlan.status() == 3:
        gpio_LED_Grn_Top.value(0)
        time.sleep(.25)
        gpio_LED_Grn_Top.value(1)
        time.sleep(.25)
        gpio_LED_Grn_Top.value(0)
        time.sleep(.25)
        gpio_LED_Grn_Top.value(1)
    else:
        gpio_LED_Grn_Top.value(0)

    # WiFi keepalive ICMP ping (enables mesh roaming)
    if KEEPALIVE_ENABLED and wlan.status() == 3:
        current_time = time.time()
        if current_time - last_ping_time >= KEEPALIVE_INTERVAL:
            wifi_keepalive_icmp_ping()
            last_ping_time = current_time

    #===== Read ALL HIGH TEMP PROBES =====
    cel_temp = (hi_sensor_TempK_1_RightIn.read())
    fer_temp_TempK_1_RightIn = (cel_temp * 1.8) + 32 + temp_calibration_TempK_1_RightIn

    cel_temp = (hi_sensor_TempK_2_LeftIn.read())
    fer_temp_TempK_2_LeftIn = (cel_temp * 1.8) + 32 + temp_calibration_TempK_2_LeftIn

    cel_temp = (hi_sensor_TempK_3_RightOut.read())
    fer_temp_TempK_3_RightOut = (cel_temp * 1.8) + 32 + temp_calibration_TempK_3_RightOut

    cel_temp = (hi_sensor_TempK_4_LeftOut.read())
    fer_temp_TempK_4_LeftOut = (cel_temp * 1.8) + 32 + temp_calibration_TempK_4_LeftOut

    #===== Track MAX temperatures over rolling window =====
    current_time = time.time()

    # TempK_1_RightIn
    elapsed_1 = current_time - max_temp_reset_time_TempK_1_RightIn
    if elapsed_1 >= MAX_TEMP_WINDOW:
        max_temp_TempK_1_RightIn = fer_temp_TempK_1_RightIn
        max_temp_reset_time_TempK_1_RightIn = current_time
    elif fer_temp_TempK_1_RightIn > max_temp_TempK_1_RightIn:
        max_temp_TempK_1_RightIn = fer_temp_TempK_1_RightIn

    # TempK_2_LeftIn
    elapsed_2 = current_time - max_temp_reset_time_TempK_2_LeftIn
    if elapsed_2 >= MAX_TEMP_WINDOW:
        max_temp_TempK_2_LeftIn = fer_temp_TempK_2_LeftIn
        max_temp_reset_time_TempK_2_LeftIn = current_time
    elif fer_temp_TempK_2_LeftIn > max_temp_TempK_2_LeftIn:
        max_temp_TempK_2_LeftIn = fer_temp_TempK_2_LeftIn

    # TempK_3_RightOut
    elapsed_3 = current_time - max_temp_reset_time_TempK_3_RightOut
    if elapsed_3 >= MAX_TEMP_WINDOW:
        max_temp_TempK_3_RightOut = fer_temp_TempK_3_RightOut
        max_temp_reset_time_TempK_3_RightOut = current_time
    elif fer_temp_TempK_3_RightOut > max_temp_TempK_3_RightOut:
        max_temp_TempK_3_RightOut = fer_temp_TempK_3_RightOut

    # TempK_4_LeftOut
    elapsed_4 = current_time - max_temp_reset_time_TempK_4_LeftOut
    if elapsed_4 >= MAX_TEMP_WINDOW:
        max_temp_TempK_4_LeftOut = fer_temp_TempK_4_LeftOut
        max_temp_reset_time_TempK_4_LeftOut = current_time
    elif fer_temp_TempK_4_LeftOut > max_temp_TempK_4_LeftOut:
        max_temp_TempK_4_LeftOut = fer_temp_TempK_4_LeftOut

    #===== Set Status and LEDs for HIGH TEMP PROBES =====
    # Probe 1 (TempK_1_RightIn) #TK1RIn
    if fer_temp_TempK_1_RightIn < under_val:
        temp_status_TempK_1_RightIn = "under"
        gpio_LED_Blu_R.on()
        gpio_LED_Grn_R.off()
        gpio_LED_Yel_R.off()
        gpio_LED_Red_R.off()
    elif under_val <= fer_temp_TempK_1_RightIn < low_val:
        temp_status_TempK_1_RightIn = "low"
        gpio_LED_Blu_R.off()
        gpio_LED_Grn_R.on()
        gpio_LED_Yel_R.off()
        gpio_LED_Red_R.off()
    elif low_val <= fer_temp_TempK_1_RightIn < high_val:
        temp_status_TempK_1_RightIn = "med"
        gpio_LED_Blu_R.off()
        gpio_LED_Grn_R.off()
        gpio_LED_Yel_R.on()
        gpio_LED_Red_R.off()
    else:
        temp_status_TempK_1_RightIn = "high"
        gpio_LED_Blu_R.off()
        gpio_LED_Grn_R.off()
        gpio_LED_Yel_R.off()
        gpio_LED_Red_R.on()

    # Probe 2 (TempK_2_LeftIn) #TK2LIn
    if fer_temp_TempK_2_LeftIn < under_val:
        temp_status_TempK_2_LeftIn = "under"
        gpio_LED_Blu_L.on()
        gpio_LED_Grn_L.off()
        gpio_LED_Yel_L.off()
        gpio_LED_Red_L.off()
    elif under_val <= fer_temp_TempK_2_LeftIn < low_val:
        temp_status_TempK_2_LeftIn = "low"
        gpio_LED_Blu_L.off()
        gpio_LED_Grn_L.on()
        gpio_LED_Yel_L.off()
        gpio_LED_Red_L.off()
    elif low_val <= fer_temp_TempK_2_LeftIn < high_val:
        temp_status_TempK_2_LeftIn = "med"
        gpio_LED_Blu_L.off()
        gpio_LED_Grn_L.off()
        gpio_LED_Yel_L.on()
        gpio_LED_Red_L.off()
    else:
        temp_status_TempK_2_LeftIn = "high"
        gpio_LED_Blu_L.off()
        gpio_LED_Grn_L.off()
        gpio_LED_Yel_L.off()
        gpio_LED_Red_L.on()

    # Probe 3 (TempK_3_RightOut) #TK3ROut
    if fer_temp_TempK_3_RightOut < under_val:
        temp_status_TempK_3_RightOut = "under"
        gpio_LED_Red_Top.off()
        gpio_LED_Yel_Top.off()
    elif under_val <= fer_temp_TempK_3_RightOut < low_val:
        temp_status_TempK_3_RightOut = "low"
        gpio_LED_Red_Top.off()
        gpio_LED_Yel_Top.on()
    elif low_val <= fer_temp_TempK_3_RightOut < high_val:
        temp_status_TempK_3_RightOut = "med"
        gpio_LED_Red_Top.off()
        gpio_LED_Yel_Top.on()
    else:
        temp_status_TempK_3_RightOut = "high"
        gpio_LED_Red_Top.on()
        gpio_LED_Yel_Top.off()

    # Probe 4 (TempK_4_LeftOut) #TK4LOut
    if fer_temp_TempK_4_LeftOut < under_val:
        temp_status_TempK_4_LeftOut = "under"
    elif under_val <= fer_temp_TempK_4_LeftOut < low_val:
        temp_status_TempK_4_LeftOut = "low"
    elif low_val <= fer_temp_TempK_4_LeftOut < high_val:
        temp_status_TempK_4_LeftOut = "med"
    else:
        temp_status_TempK_4_LeftOut = "high"

    #===== Track OVERTEMP Events (independent 20-minute hold) =====
    current_time = time.time()

    # TempK_1_RightIn overtemp tracking
    if temp_status_TempK_1_RightIn == "high":
        if not overtemp_flag_TempK_1_RightIn:
            overtemp_flag_TempK_1_RightIn = True
            overtemp_max_TempK_1_RightIn = fer_temp_TempK_1_RightIn
            overtemp_start_time_TempK_1_RightIn = current_time
        elif fer_temp_TempK_1_RightIn > overtemp_max_TempK_1_RightIn:
            overtemp_max_TempK_1_RightIn = fer_temp_TempK_1_RightIn

    if overtemp_flag_TempK_1_RightIn and (current_time - overtemp_start_time_TempK_1_RightIn) >= MAX_TEMP_WINDOW:
        overtemp_flag_TempK_1_RightIn = False

    # TempK_2_LeftIn overtemp tracking
    if temp_status_TempK_2_LeftIn == "high":
        if not overtemp_flag_TempK_2_LeftIn:
            overtemp_flag_TempK_2_LeftIn = True
            overtemp_max_TempK_2_LeftIn = fer_temp_TempK_2_LeftIn
            overtemp_start_time_TempK_2_LeftIn = current_time
        elif fer_temp_TempK_2_LeftIn > overtemp_max_TempK_2_LeftIn:
            overtemp_max_TempK_2_LeftIn = fer_temp_TempK_2_LeftIn

    if overtemp_flag_TempK_2_LeftIn and (current_time - overtemp_start_time_TempK_2_LeftIn) >= MAX_TEMP_WINDOW:
        overtemp_flag_TempK_2_LeftIn = False

    # TempK_3_RightOut overtemp tracking
    if temp_status_TempK_3_RightOut == "high":
        if not overtemp_flag_TempK_3_RightOut:
            overtemp_flag_TempK_3_RightOut = True
            overtemp_max_TempK_3_RightOut = fer_temp_TempK_3_RightOut
            overtemp_start_time_TempK_3_RightOut = current_time
        elif fer_temp_TempK_3_RightOut > overtemp_max_TempK_3_RightOut:
            overtemp_max_TempK_3_RightOut = fer_temp_TempK_3_RightOut

    if overtemp_flag_TempK_3_RightOut and (current_time - overtemp_start_time_TempK_3_RightOut) >= MAX_TEMP_WINDOW:
        overtemp_flag_TempK_3_RightOut = False

    # TempK_4_LeftOut overtemp tracking
    if temp_status_TempK_4_LeftOut == "high":
        if not overtemp_flag_TempK_4_LeftOut:
            overtemp_flag_TempK_4_LeftOut = True
            overtemp_max_TempK_4_LeftOut = fer_temp_TempK_4_LeftOut
            overtemp_start_time_TempK_4_LeftOut = current_time
        elif fer_temp_TempK_4_LeftOut > overtemp_max_TempK_4_LeftOut:
            overtemp_max_TempK_4_LeftOut = fer_temp_TempK_4_LeftOut

    if overtemp_flag_TempK_4_LeftOut and (current_time - overtemp_start_time_TempK_4_LeftOut) >= MAX_TEMP_WINDOW:
        overtemp_flag_TempK_4_LeftOut = False

    #===== BUZZER CONTROL - TempK_1_RightIn and TempK_2_LeftIn =====
    # Per-iteration buzzer logic - works like WiFi LED blink (once per loop)

    # TempK_1_RightIn buzzer
    if temp_status_TempK_1_RightIn != previous_status_TempK_1_RightIn:
        # Status changed - detect transition type
        if (previous_status_TempK_1_RightIn == "low" and temp_status_TempK_1_RightIn == "med"):
            # Green to Yellow transition
            transition_beep_TempK_1_RightIn = True
        elif (previous_status_TempK_1_RightIn == "med" and temp_status_TempK_1_RightIn == "low"):
            # Yellow to Green transition
            transition_beep_TempK_1_RightIn = True
        else:
            # Any other transition (including to/from red)
            transition_beep_TempK_1_RightIn = False
        previous_status_TempK_1_RightIn = temp_status_TempK_1_RightIn

    # Beep for transition (once per transition)
    if transition_beep_TempK_1_RightIn:
        if temp_status_TempK_1_RightIn == "med":
            # Green to Yellow: single full beep
            beep(BEEP_DURATION)
        elif temp_status_TempK_1_RightIn == "low":
            # Yellow to Green: 1/4 beep
            beep(BEEP_DURATION / 4)
        transition_beep_TempK_1_RightIn = False

    # Red alert: 3 beeps separated by 0.5 seconds (each iteration)
    if temp_status_TempK_1_RightIn == "high":
        beep(BEEP_DURATION)
        time.sleep(0.5)
        beep(BEEP_DURATION)
        time.sleep(0.5)
        beep(BEEP_DURATION)

    # TempK_2_LeftIn buzzer
    if temp_status_TempK_2_LeftIn != previous_status_TempK_2_LeftIn:
        # Status changed - detect transition type
        if (previous_status_TempK_2_LeftIn == "low" and temp_status_TempK_2_LeftIn == "med"):
            # Green to Yellow transition
            transition_beep_TempK_2_LeftIn = True
        elif (previous_status_TempK_2_LeftIn == "med" and temp_status_TempK_2_LeftIn == "low"):
            # Yellow to Green transition
            transition_beep_TempK_2_LeftIn = True
        else:
            # Any other transition (including to/from red)
            transition_beep_TempK_2_LeftIn = False
        previous_status_TempK_2_LeftIn = temp_status_TempK_2_LeftIn

    # Beep for transition (once per transition)
    if transition_beep_TempK_2_LeftIn:
        if temp_status_TempK_2_LeftIn == "med":
            # Green to Yellow: single full beep
            beep(BEEP_DURATION)
        elif temp_status_TempK_2_LeftIn == "low":
            # Yellow to Green: 1/4 beep
            beep(BEEP_DURATION / 4)
        transition_beep_TempK_2_LeftIn = False

    # Red alert: 3 beeps separated by 0.5 seconds (each iteration)
    if temp_status_TempK_2_LeftIn == "high":
        beep(BEEP_DURATION)
        time.sleep(0.5)
        beep(BEEP_DURATION)
        time.sleep(0.5)
        beep(BEEP_DURATION)

    #===== Read ALL LOW TEMP PROBES =====
    ds_sensor.convert_temp()
    time.sleep(0.75)
    low_temps_data = []
    for idx, rom in enumerate(low_roms, 1):
        cel_temp = ds_sensor.read_temp(rom)
        fer_temp_low = (cel_temp * 1.8) + 32
        # Apply calibration
        if idx == 1:
            fer_temp_low += temp_calibration_low1
            probe_name = "TempLow1"
        elif idx == 2:
            fer_temp_low += temp_calibration_low2
            probe_name = "TempLow2"
        elif idx == 3:
            fer_temp_low += temp_calibration_low3
            probe_name = "TempLow3"
        elif idx == 4:
            fer_temp_low += temp_calibration_low4
            probe_name = "TempLow4"

        # Calculate status for low temp probe
        if fer_temp_low < under_val:
            temp_status_low = "under"
        elif under_val <= fer_temp_low < low_val:
            temp_status_low = "low"
        elif low_val <= fer_temp_low < high_val:
            temp_status_low = "med"
        else:
            temp_status_low = "high"

        low_temps_data.append({"name": probe_name, "temp": fer_temp_low, "status": temp_status_low})

    # Get Wi-Fi signal strength
    signal_strength = wlan.status('rssi')
    wifi_status = "CONNECTED" if wlan.status() == 3 else "OFFLINE"

    # ===== Print Summary to Console =====
    print(f"\n[MONITOR] HighTemp:")
    ot1_flag = " *OVERTEMP*" if overtemp_flag_TempK_1_RightIn else ""
    ot2_flag = " *OVERTEMP*" if overtemp_flag_TempK_2_LeftIn else ""
    ot3_flag = " *OVERTEMP*" if overtemp_flag_TempK_3_RightOut else ""
    ot4_flag = " *OVERTEMP*" if overtemp_flag_TempK_4_LeftOut else ""
    print(f"  TempK_1_RightIn = {fer_temp_TempK_1_RightIn:.1f}°F [{temp_status_TempK_1_RightIn}] Max: {max_temp_TempK_1_RightIn:.1f}°F{ot1_flag}")
    if overtemp_flag_TempK_1_RightIn:
        print(f"    └─ Overtemp Event Max: {overtemp_max_TempK_1_RightIn:.1f}°F")
    print(f"  TempK_2_LeftIn  = {fer_temp_TempK_2_LeftIn:.1f}°F [{temp_status_TempK_2_LeftIn}] Max: {max_temp_TempK_2_LeftIn:.1f}°F{ot2_flag}")
    if overtemp_flag_TempK_2_LeftIn:
        print(f"    └─ Overtemp Event Max: {overtemp_max_TempK_2_LeftIn:.1f}°F")
    print(f"  TempK_3_RightOut = {fer_temp_TempK_3_RightOut:.1f}°F [{temp_status_TempK_3_RightOut}] Max: {max_temp_TempK_3_RightOut:.1f}°F{ot3_flag}")
    if overtemp_flag_TempK_3_RightOut:
        print(f"    └─ Overtemp Event Max: {overtemp_max_TempK_3_RightOut:.1f}°F")
    print(f"  TempK_4_LeftOut  = {fer_temp_TempK_4_LeftOut:.1f}°F [{temp_status_TempK_4_LeftOut}] Max: {max_temp_TempK_4_LeftOut:.1f}°F{ot4_flag}")
    if overtemp_flag_TempK_4_LeftOut:
        print(f"    └─ Overtemp Event Max: {overtemp_max_TempK_4_LeftOut:.1f}°F")

    print(f"\n[MONITOR] LowTemp:")
    for probe in low_temps_data:
        print(f"  {probe['name']} = {probe['temp']:.1f}°F [{probe['status']}]")

    print(f"\nWiFi: {wifi_status} ({signal_strength} dBm)")

    # ========== WATCHDOG TEST ==========
    if TEST_WATCHDOG:
        print("\n[TEST] Hanging for watchdog test...")
        print("[TEST] Pico will reboot in ~8 seconds...")
        time.sleep(10)  # Trigger watchdog timeout

    # ============ Print data on LCD ============
    lcd.clear()

    # Line 1: TK4 (Left) actual/max and TK3 (Right) actual/max
    line1 = "OL{:.0f}/{:.0f} R{:.0f}/{:.0f}".format(fer_temp_TempK_4_LeftOut, max_temp_TempK_4_LeftOut, fer_temp_TempK_3_RightOut, max_temp_TempK_3_RightOut)
    lcd.putstr(line1)

    # Line 2: TK2 (InLeft) actual/max and TK1 (InRight) actual/max
    lcd.move_to(0, 1)
    line2 = "IL{:.0f}/{:.0f} R{:.0f}/{:.0f}".format(fer_temp_TempK_2_LeftIn, max_temp_TempK_2_LeftIn, fer_temp_TempK_1_RightIn, max_temp_TempK_1_RightIn)
    lcd.putstr(line2)

    # Line 3: Low temp probes a=TempLow1, b=TempLow2, c=TempLow3, d=TempLow4
    lcd.move_to(0, 2)
    line3 = "a{:.0f} b{:.0f} c{:.0f} d{:.0f}".format(low_temps_data[0]['temp'], low_temps_data[1]['temp'], low_temps_data[2]['temp'], low_temps_data[3]['temp'])
    lcd.putstr(line3)

    # Line 4: WiFi Signal Strength and IP Address
    lcd.move_to(0, 3)
    if wlan.status() == 3:
        line4 = "{0:}db {1}".format(signal_strength, ip_address)
    else:
        line4 = "WiFi: OFFLINE"
    lcd.putstr(line4)


    # Check if resend timeout elapsed
    elapsed_time = time.time() - start_time
    if elapsed_time >= resend_email_interval:
        already_sent = 0

    # ========== Check for Alert Condition ==========
    if (temp_status_TempK_1_RightIn == "high" or temp_status_TempK_2_LeftIn == "high" or temp_status_TempK_3_RightOut == "high" or temp_status_TempK_4_LeftOut == "high") and already_sent != 1:
        print(f"\n[ALERT] HIGH TEMPERATURE DETECTED")
        if EMAIL_ENABLED:
            print(f"[ALERT] Sending email alert...")
        else:
            print(f"[ALERT] Email notifications disabled (EMAIL_ENABLED=False)")

        already_sent = 1 #indicate we've just sent an email and wont do it again until we timeout
        start_time = time.time()  # Record the start time that this email was sent

        #Email details
        if EMAIL_ENABLED:
            try:
                sender_email = config.SENDER_EMAIL
                sender_name = config.SENDER_NAME
                sender_app_password = config.SENDER_APP_PASSWORD
                recipient_email = config.RECIPIENT_EMAIL
    #            recipient_email = ''
                email_subject = 'High Temp Alert'

                ##### Test Send one email #####
                #Send the email
                #Connect to the SMTP server
                smtp = umail.SMTP(config.SMTP_SERVER, config.SMTP_PORT, ssl=config.SMTP_SSL)
                smtp.login(sender_email, sender_app_password)
                smtp.to(recipient_email)

                smtp.write("From:" + sender_name + "<"+ sender_email+">\n")
                smtp.write("Subject:" + email_subject + "\n")
                smtp.write("\n")  # Blank line to separate headers from body

                email_temp_1 = "{:.0f}".format(fer_temp_TempK_1_RightIn)
                email_temp_2 = "{:.0f}".format(fer_temp_TempK_2_LeftIn)
                email_temp_3 = "{:.0f}".format(fer_temp_TempK_3_RightOut)
                email_temp_4 = "{:.0f}".format(fer_temp_TempK_4_LeftOut)

                # Now write the body
                smtp.write(f"TK1: {email_temp_1}\nTK2: {email_temp_2}\nTK3: {email_temp_3}\nTK4: {email_temp_4}\n\nDiesel Heat Alert: Raspberry Pi Pico W")
                #send the email

                smtp.send()
                smtp.quit()
                print("[ALERT] Email sent successfully")
            except Exception as e:
                print(f"[ALERT] Email failed: {e}")

    if WATCHDOG_ENABLED:
        watchdog.feed()  # Feed watchdog to prevent auto-reboot

