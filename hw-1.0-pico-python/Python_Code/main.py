# TempAlerter Type K x2
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

from machine import I2C, Pin
import time
from max6675 import MAX6675
import network
import connect_to_internet  #via wifi (credentials in config.py)
import umail
import config
from lcd_pico_i2c import I2cLcd

#import utime

# ******************* CONSTANTS ********************

already_sent = 1  # 1 = no email, 0 = primed to send a single email
resend_email_interval = 120 # in seconds, and only if conditions are still there


# ****************   Temp Range Values
# All values are in degrees Fahrenheit.
# The right values depend on what you are measuring and when you want an
# alert, so set them for your own application. The values below are examples.
# Example: Blue < 192, Green 192 to 230, Yellow 230 to 245, Red (high) > 250
# Original Values
#under_val = 192
#low_val = 234
#high_val = 247

# Updated Values
#under_val = 180
#low_val = 227
#high_val = 235

# Test values (default): low enough to trigger by holding a probe between
# your fingers, so you can verify the LEDs, LCD and email alert during setup.
# Switch to your own operating values (such as the examples above) for real use.
under_val = 76
low_val = 82
high_val = 85


temp_calibration_left = 0
temp_calibration_right = 0


####################### DEFINITIONS ###################


# *********** Set up 2x16 Display *********
# Initialize the I2C bus (this can get moved up if the i2c bus is being used for other things too)
# I2C0 Specify the SCL and SDA pins
scl_pin0 = Pin(1)  # SCL on GP1 (Pin 2)
sda_pin0 = Pin(0)  # SDA on GP0 (Pin 1)
i2c0 = I2C(0, scl=scl_pin0, sda=sda_pin0, freq=400000)

I2C_DISP_ADDR = 39
lcd = I2cLcd(i2c0, I2C_DISP_ADDR, 2, 16)

# LCD display's cursor to flash (blink) on and off
#lcd.blink_cursor_on()

lcd.backlight_on()
lcd.clear()  # clear here since display gets filled and I don't like the refresh look

# Enumerate I2C0 bus for troubleshooting
#I2C_ADDR = i2c0.scan()[0]  # first item only, if multiple you will need to enumerate differently
#print("I2C0 Bus Items: ",I2C_ADDR)


lcd.putstr("booting....") 


# *********** Initialize LED Variables ***********
# Onboard LED (not used since covered)
#myLED=Pin('LED',Pin.OUT)

# Top LEDs
# D2 Blue, Top (not currently used)
gpio_LED_Blu_Top=Pin(12,Pin.OUT)
gpio_LED_Blu_Top.value(0)
# D3 Green, Top (WiFi connected)
gpio_LED_Grn_Top=Pin(13,Pin.OUT)
gpio_LED_Grn_Top.value(0)
# D4 Yellow, Top (not currently used)
gpio_LED_Yel_Top=Pin(14,Pin.OUT)
gpio_LED_Yel_Top.value(0)
# D5 Red, Top (WiFi down)
gpio_LED_Red_Top=Pin(15,Pin.OUT)
gpio_LED_Red_Top.value(0)


# Left Lower LEDs
# D13 Blue, Left Bottom (Left temp under)
gpio_LED_Blu_L=Pin(26,Pin.OUT)
gpio_LED_Blu_L.value(0)
# D12 Green, Left Bottom (Left temp low)
gpio_LED_Grn_L=Pin(22,Pin.OUT)
gpio_LED_Grn_L.value(0)
# D11 Yellow, Left Bottom (Left temp med)
gpio_LED_Yel_L=Pin(21,Pin.OUT)
gpio_LED_Yel_L.value(0)
# D10 Red, Left Bottom (Left temp high)
gpio_LED_Red_L=Pin(20,Pin.OUT)
gpio_LED_Red_L.value(0)

# Right Lower LEDs
# D6 Blue, Right Bottom (Right temp under)
gpio_LED_Blu_R=Pin(16,Pin.OUT)
gpio_LED_Blu_R.value(0)
# D7 Green, Right Bottom (Right temp low)
gpio_LED_Grn_R=Pin(17,Pin.OUT)
gpio_LED_Grn_R.value(0)
# D8 Yellow, Right Bottom (Right temp med)
gpio_LED_Yel_R=Pin(18,Pin.OUT)
gpio_LED_Yel_R.value(0)
# D9 Red, Right Bottom (Right temp high)
gpio_LED_Red_R=Pin(19,Pin.OUT)
gpio_LED_Red_R.value(0)







# *********** Set up network DHCP ***********
# Test network info code
gpio_LED_Grn_Top.value(0)
wlan = network.WLAN(network.STA_IF)
ip_address = wlan.ifconfig()[0]
print ('WLAN=', wlan.status())
# Display the IP address
print("Your IP address is:", ip_address)
if wlan.status() == 3:
    gpio_LED_Grn_Top.value(1)
    print ("gpio_LED_Grn_Top onboard = 1 on which means wifi=3 which is on")
    
    # Get Wi-Fi signal strength (RSSI)
    signal_strength = wlan.status('rssi')
    print("Wi-Fi Signal Strength (RSSI):", signal_strength, "dBm")

#   -30 dBm to -50 dBm: Excellent signal (strong and stable connection).
#   -51 dBm to -60 dBm: Good signal (reliable connection).
#   -61 dBm to -70 dBm: Fair signal (may be somewhat slower or less reliable, but should work for most uses).
#   -71 dBm to -80 dBm: Weak signal (connection may be slow or have occasional dropouts).
#   Below -80 dBm: Very weak signal (connection may be unstable, with frequent dropouts).

else:
    gpio_LED_Red_Top.value(1)
    print ("Woops, the wifi is down")




# *********** Initialize Temp Sensors ***********
# High temp sensor code *LEFT*
sck = Pin(5, Pin.OUT)
cs = Pin(6, Pin.OUT)
so = Pin(7, Pin.IN)
hi_sensor_left = MAX6675(sck, cs , so)

# High temp sensor code *RIGHT*
sck = Pin(2, Pin.OUT)
cs = Pin(3, Pin.OUT)
so = Pin(4, Pin.IN)
hi_sensor_right = MAX6675(sck, cs , so)

# Stabilization loop, sometimes the first readings from the probes are off
# This allows better readings
counter = 0
while counter < 3:


    #----- HIGH TEMP PROBE LEFT -----
    cel_temp = (hi_sensor_left.read())
    fer_temp_left = (cel_temp * 1.8) + 32
    print("===== STABLE High-TEMP_LEFT: temperature F =",fer_temp_left,"\n")

    #----- HIGH TEMP PROBE RIGHT -----
    cel_temp = (hi_sensor_right.read())
    fer_temp_right = (cel_temp * 1.8) + 32
    print("===== STABLE: High-TEMP_RIGHT: temperature F =",fer_temp_right)


    time.sleep(1)
    counter += 1


start_time = time.time()  # Initialize start time entering the loop


############################# DO THE WORK ########################
while True:    
    
    # Check that WiFi is running and blink the top green LED (GP13)
    if wlan.status() == 3:
        gpio_LED_Grn_Top.value(0)
        time.sleep(.25)
        gpio_LED_Grn_Top.value(1)
        time.sleep(.25)
        gpio_LED_Grn_Top.value(0)
        time.sleep(.25)
        gpio_LED_Grn_Top.value(1)
        
        print ("wifi=3 which is on. IP = ", ip_address)
    else:
        gpio_LED_Grn_Top.value(0)
        print ("Woops, the wifi is down")
    
    #----- HIGH TEMP PROBE LEFT -----
    cel_temp = (hi_sensor_left.read())
    fer_temp_left = (cel_temp * 1.8) + 32
    fer_temp_left += temp_calibration_left
     #print("High-TEMP: temperature C =",cel_temp)
    print("High-TEMP_LEFT: temperature F =",fer_temp_left)
    time.sleep(1)

    #fer_temp_left = 210 #test value

    ### Set LEDs based on temp range
    if fer_temp_left < under_val:
        temp_status_left = "under"
    elif under_val <= fer_temp_left < low_val:
        temp_status_left = "low"
    elif low_val <= fer_temp_left < high_val:
        temp_status_left = "med"
    else:
        temp_status_left = "high"

    print ("TEMP STATUS Value Left:", temp_status_left)
  
    # LEFT LEDs: light one LED for temp status (Blue=under, Green=low, Yellow=med, Red=high)


    if temp_status_left == "under":
        gpio_LED_Blu_L.on()
        gpio_LED_Grn_L.off()
        gpio_LED_Yel_L.off()
        gpio_LED_Red_L.off()
    elif temp_status_left == "low":
        gpio_LED_Blu_L.off()
        gpio_LED_Grn_L.on()
        gpio_LED_Yel_L.off()
        gpio_LED_Red_L.off()
    elif temp_status_left == "med":
        gpio_LED_Blu_L.off()
        gpio_LED_Grn_L.off()
        gpio_LED_Yel_L.on()
        gpio_LED_Red_L.off()
    elif temp_status_left == "high":
        gpio_LED_Blu_L.off()
        gpio_LED_Grn_L.off()
        gpio_LED_Yel_L.off()
        gpio_LED_Red_L.on()




    #----- HIGH TEMP PROBE RIGHT -----
    cel_temp = (hi_sensor_right.read())
    fer_temp_right = (cel_temp * 1.8) + 32
    fer_temp_right += temp_calibration_right
    #print("High-TEMP: temperature C =",cel_temp)
    print("High-TEMP_RIGHT: temperature F =",fer_temp_right,"\n")
    time.sleep(1)


    #fer_temp_right = 239  #test value

    ### Set LEDs based on temp range
    if fer_temp_right < under_val:
        temp_status_right = "under"
    elif under_val <= fer_temp_right < low_val:
        temp_status_right = "low"
    elif low_val <= fer_temp_right < high_val:
        temp_status_right = "med"
    else:
        temp_status_right = "high"

    print ("TEMP STATUS Value Right:", temp_status_right)
  
    # RIGHT LEDs: light one LED for temp status (Blue=under, Green=low, Yellow=med, Red=high)

    if temp_status_right == "under":
        gpio_LED_Blu_R.on()
        gpio_LED_Grn_R.off()
        gpio_LED_Yel_R.off()
        gpio_LED_Red_R.off()
    elif temp_status_right == "low":
        gpio_LED_Blu_R.off()
        gpio_LED_Grn_R.on()
        gpio_LED_Yel_R.off()
        gpio_LED_Red_R.off()
    elif temp_status_right == "med":
        gpio_LED_Blu_R.off()
        gpio_LED_Grn_R.off()
        gpio_LED_Yel_R.on()
        gpio_LED_Red_R.off()
    elif temp_status_right == "high":
        gpio_LED_Blu_R.off()
        gpio_LED_Grn_R.off()
        gpio_LED_Yel_R.off()
        gpio_LED_Red_R.on()

    
    # Get updated Wi-Fi signal strength (RSSI)
    signal_strength = wlan.status('rssi')
    print("Wi-Fi Signal Strength (RSSI):", signal_strength, "dBm")

    # ************** Print data on LCD **************
    lcd.clear()

    # Build strings to print on the LCD
    # TOP LINE
    message_left_temp = "L {:.0f}".format(fer_temp_left)
    message_top_space = "  "
    message_right_temp = "R {:.0f}".format(fer_temp_right)
        #message_temperature_int = " {:.0f}F ".format(tempF_i1)
        #message_dewpoint_int = "d{:.1f}".format(dewpointF_int)

    # BOTTOM LINE
    message_bot = f"{signal_strength} {ip_address}"
        #message_temperature_ext = " t{:.0f}F".format(last_temperature)
        #message_dewpoint_ext = " d{:.1f}%".format(dewpointF_ext)

    # First line
    lcd.putstr(message_left_temp)
    lcd.putstr(message_top_space)
    lcd.putstr(message_right_temp)
    #lcd.putstr(message_temperature_int)
    
    # Second line
    # Move the cursor to the second line
    lcd.move_to(0, 1)
    lcd.putstr(message_bot)
        #lcd.putstr(message_temperature_ext)


    # After resend_email_interval seconds, allow another email

    # Check the elapsed time
    elapsed_time = time.time() - start_time
    if elapsed_time >= resend_email_interval:  # default 120 seconds = 2 minutes
         already_sent = 0  # Re-arm so another email can be sent

        
    print ("eTime: ", elapsed_time, "sTime:", start_time , ":AlreadySent =", already_sent)

 
# *********** Send an email if things are high ***********
    if (temp_status_left == "high" or temp_status_right == "high") and already_sent != 1:
        print ("Sending an Email: <<<<<<<<<<<<<<<<<<<", fer_temp_left, fer_temp_right)
        already_sent = 1 # indicate we've just sent an email and won't do it again until we time out
        start_time = time.time()  # Record the start time that this email was sent
        
        # Email details
        try:
            sender_email = config.SENDER_EMAIL
            sender_name = config.SENDER_NAME
            sender_app_password = config.SENDER_APP_PASSWORD
            recipient_email = config.RECIPIENT_EMAIL
#            recipient_email = ''
            email_subject = 'High Temp Alert'

            ##### Test Send one email #####
            # Send the email
            # Connect to Gmail's SSL port
            smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True)
            smtp.login(sender_email, sender_app_password)
            smtp.to(recipient_email)

            smtp.write("From:" + sender_name + "<"+ sender_email+">\n")
            smtp.write("Subject:" + email_subject + "\n")
            smtp.write("\n")  # Blank line to separate headers from body

            email_left_temp = "{:.0f}".format(fer_temp_left)
            email_right_temp = "{:.0f}".format(fer_temp_right)


            # Now write the body
            smtp.write(f"L: {email_left_temp}\nR: {email_right_temp}\n\nDiesel Heat Alert: Virgil's Raspberry Pi Pico W")
            #smtp.write("Left: ", fer_temp_left, "Right: ", fer_temp_right, "/nDiesel Heat Alert: Virgil's Raspberry Pi Pico W")
            # Send the email

            smtp.send()
            smtp.quit()
            print('Email Sent')
        except Exception as e:
            print("Failed to send email:", e)
   
    else:
        # Do nothing if already_sent is 1 or condition is not met
        pass  
  



