# TempAlerter Type K x4 - MAXI - ALPHA
# Copyright (C) 2026 Virgil Mehalek
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed WITHOUT ANY WARRANTY; see
# the LICENSE file or <https://www.gnu.org/licenses/> for details.

# Test script for WiFi ICMP ping functionality

import network
import time
import config
from wifi_ping import icmp_ping

print("[TEST] WiFi ICMP Ping Test")
print("=" * 50)

# Connect to WiFi
print("\n[TEST] Connecting to WiFi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

attempt = 0
while wlan.status() != 3 and attempt < 15:
    attempt += 1
    print(f"  Attempt {attempt}/15...", end="")
    time.sleep(1)
    print(f" Status: {wlan.status()}")

if wlan.status() == 3:
    print("\n[TEST] WiFi Connected!")
    ip_info = wlan.ifconfig()
    print(f"  IP Address: {ip_info[0]}")
    print(f"  Netmask: {ip_info[1]}")
    print(f"  Gateway: {ip_info[2]}")
    gateway = ip_info[2]
else:
    print("\n[TEST] WiFi Connection Failed!")
    exit()

# Test 1: Single ping
print("\n[TEST] Test 1: Single ping to gateway")
print("-" * 50)
sent, received = icmp_ping(gateway, count=1, timeout=2000)
print(f"  Sent: {sent}, Received: {received}")
if received > 0:
    print("  ✓ PASS")
else:
    print("  ✗ FAIL")

# Test 2: Multiple pings
print("\n[TEST] Test 2: Multiple pings (3) to gateway")
print("-" * 50)
sent, received = icmp_ping(gateway, count=3, timeout=2000)
print(f"  Sent: {sent}, Received: {received}")
if received > 0:
    print(f"  ✓ PASS ({received}/{sent} successful)")
else:
    print("  ✗ FAIL")

# Test 3: Ping external host
print("\n[TEST] Test 3: Ping external host (8.8.8.8)")
print("-" * 50)
sent, received = icmp_ping("8.8.8.8", count=1, timeout=2000)
print(f"  Sent: {sent}, Received: {received}")
if received > 0:
    print("  ✓ PASS")
else:
    print("  ✗ FAIL (or no internet)")

print("\n[TEST] All tests complete")
print("=" * 50)
