TempAlerter Type K x2 - v1.1
Hardware v1.0 Two type K probes, 12 LED's and an LCD display.


WHAT IT DOES
------------
TempAlerter is a two-channel high-temperature monitor and alarm built on a
Raspberry Pi Pico W running MicroPython.

- Reads two Type K thermocouples (Left and Right) through MAX6675 boards,
  in degrees F, with a per-probe calibration offset.
- Sorts each reading into one of four ranges (under / low / med / high) and
  lights the matching LED on that side: Blue, Green, Yellow, or Red.
- Shows both temperatures on a 16x2 LCD (top line), with the WiFi signal
  strength and the Pico's IP address on the bottom line.
- Connects to WiFi at startup. The top green LED stays lit (with a quick
  flicker each update) while WiFi is up; the top red LED lights if WiFi is
  down at startup.
- Sends an email alert through Gmail (SMTP over SSL) when either probe
  reaches the "high" range. While it stays high, the alert repeats at most
  once every resend_email_interval seconds (default 120).

Setup notes:
- WiFi and email credentials go in config.py (use a Gmail app password).
  Keep real values out of anything you share.
- main.py ships with room-temperature TEST thresholds (under_val, low_val,
  high_val near the top of the file). Hold a probe between your fingers to
  reach the "high" range and trigger the red LED and an email alert. Once
  setup is verified, set your own operating values.
- The right thresholds depend on what you are measuring and when you want to
  be alerted. The commented-out values in main.py are examples only. All
  temperatures are in degrees Fahrenheit.
- Upload all files in Python_Code_Place_On_Pico/ to the root of the Pico W
  (e.g. with Thonny). main.py runs automatically at power-up.
- Test_Code/ holds standalone test scripts for future hardware (DS18B20
  probes, buzzer, 5-LED top row). They are not needed on the Pico.

Wiring, pin assignments, and planned future hardware (buzzer, DS18B20
low-temp probes, 5-LED top row) are documented in CLAUDE.md, the schematic
images, and parts_list.txt.


LICENSE
-------
Copyright (C) 2026 Virgil Mehalek

TempAlerter is free software, licensed under the GNU General Public License
v3.0 or later. See the LICENSE file for the full text.


CREDITS
-------
These third-party libraries in Python_Code_Place_On_Pico/ are used under the MIT
License.
Full license notices are in THIRD_PARTY_LICENSES.txt.

- lcd_api.py       Dave Hylands        https://github.com/dhylands/python_lcd
- lcd_pico_i2c.py  Tyler Peppy         https://github.com/T-622/RPI-PICO-I2C-LCD
                   (based on Dave Hylands' python_lcd)
- max6675.py       Ivan Sevcik         https://github.com/BetaRavener/micropython-hw-lib
- umail.py         Shawwwn             https://github.com/shawwwn/uMail


DISCLAIMER
----------
This is a personal hobby project, provided "as is" without warranty of any
kind. Use it at your own risk.

It is NOT designed, tested, or certified for life-safety, fire-protection,
medical, or other critical uses, and must not be relied on to protect people,
animals, or property. Temperature readings may be inaccurate, and alerts
(LEDs, display, and email) can be delayed or fail entirely because of sensor,
wiring, WiFi, power, or software faults.

Always use properly certified safety devices (smoke and CO detectors, thermal
cutoffs, etc.) for anything that matters. The author accepts no liability for
any damage, injury, or loss resulting from use of this code or hardware
design.
