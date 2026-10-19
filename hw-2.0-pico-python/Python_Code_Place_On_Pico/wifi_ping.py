# wifi_ping.py - ICMP ping utility for Pico W WiFi keepalive
# Source: https://github.com/bokunimowakaru/ping (adapted)
# Copyright (c) 2023 Wataru KUNINO
# SPDX-License-Identifier: MIT
# Full license text: see THIRD_PARTY_LICENSES.txt

import socket
import time

def checksum_calc(payload):
    """Calculate ICMP checksum per RFC 792"""
    if len(payload) % 2 == 1:
        payload += b'\x00'
    cs = 0x0000
    for i in range(len(payload) // 2):
        cs += int(payload[i*2]) * 256
        cs += int(payload[i*2+1])
        if cs > 0xFFFF:
            cs += 1
            cs &= 0xFFFF
    cs = ~(cs) & 0xFFFF
    return cs.to_bytes(2, 'big')

def icmp_ping(host, count=3, timeout=2000):
    """
    Send ICMP echo requests to host
    Returns: (pings_sent, pings_received)
    """
    icm_type = b'\x08'      # ICMP echo request
    icm_code = b'\x00'      # Code = 0
    icm_idnt = b'\x12\x34'  # Identifier
    body = b'MicroPython'   # Payload

    pings_sent = 0
    pings_received = 0

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, 1)
        sock.settimeout(timeout / 1000)
    except Exception as e:
        print(f"[PING] Socket creation failed: {e}")
        return (0, 0)

    for seq in range(1, count + 1):
        try:
            # Build ICMP header
            icm_snum = seq.to_bytes(2, 'big')
            header = icm_type + icm_code + b'\x00\x00' + icm_idnt + icm_snum

            # Calculate checksum
            payload = header + body
            checksum = checksum_calc(payload)

            # Rebuild header with checksum
            header = icm_type + icm_code + checksum + icm_idnt + icm_snum
            payload = header + body

            # Send ping
            sock.sendto(payload, (host, 0))
            pings_sent += 1

            # Wait for response
            try:
                icmp_response = sock.recv(256)
                # Validate response
                if len(icmp_response) >= 28:
                    protocol = icmp_response[9]
                    icmp_type = icmp_response[20]
                    if protocol == 0x01 and icmp_type == 0x00:  # ICMP echo reply
                        pings_received += 1
            except socket.timeout:
                pass  # No response, continue

            # Small delay between pings
            if seq < count:
                time.sleep(0.1)

        except Exception as e:
            print(f"[PING] Error sending ping {seq}: {e}")

    sock.close()
    return (pings_sent, pings_received)
