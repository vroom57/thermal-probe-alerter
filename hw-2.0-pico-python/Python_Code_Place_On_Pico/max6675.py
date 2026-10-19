# max6675.py - MAX6675 Type K thermocouple driver
# Source: https://github.com/BetaRavener/micropython-hw-lib (MAX6675/max6675.py)
# Copyright (c) 2016 Ivan Sevcik
# Modified 2026 by Virgil Mehalek: SCK and SO are shared class-level pins so
# several MAX6675 boards can share one bus, each with its own CS pin.
# SPDX-License-Identifier: MIT
# Full license text: see THIRD_PARTY_LICENSES.txt

import time
class MAX6675:
    MEASUREMENT_PERIOD_MS = 220

    def __init__(self, cs, sck=None, so=None):
        """
        Creates new object for controlling MAX6675
        :param cs: CS (select) pin, must be configured as Pin.OUT (unique per sensor)
        :param sck: SCK (clock) pin, must be configured as Pin.OUT (shared across sensors)
        :param so: SO (data) pin, must be configured as Pin.IN (shared across sensors)
        Note: If sck and so are None, they should be set as class variables before creating instances
        """
        # Thermocouple
        self._cs = cs
        self._cs.high()

        # Store class-level shared pins if provided
        if sck is not None:
            MAX6675._sck = sck
            MAX6675._sck.low()
        if so is not None:
            MAX6675._so = so
            MAX6675._so.low()

        self._last_measurement_start = 0
        self._last_read_temp = 0
        self._error = 0

    def _cycle_sck(self):
        MAX6675._sck.high()
        time.sleep_us(1)
        MAX6675._sck.low()
        time.sleep_us(1)

    def refresh(self):
        """
        Start a new measurement.
        """
        self._cs.low()
        time.sleep_us(10)
        self._cs.high()
        self._last_measurement_start = time.ticks_ms()

    def ready(self):
        """
        Signals if measurement is finished.
        :return: True if measurement is ready for reading.
        """
        return time.ticks_ms() - self._last_measurement_start > MAX6675.MEASUREMENT_PERIOD_MS

    def error(self):
        """
        Returns error bit of last reading. If this bit is set (=1), there's problem with the
        thermocouple - it can be damaged or loosely connected
        :return: Error bit value
        """
        return self._error

    def read(self):
        """
        Reads last measurement and starts a new one. If new measurement is not ready yet, returns last value.
        Note: The last measurement can be quite old (e.g. since last call to `read`).
        To refresh measurement, call `refresh` and wait for `ready` to become True before reading.
        :return: Measured temperature
        """
        # Check if new reading is available
        if self.ready():
            # Bring CS pin low to start protocol for reading result of
            # the conversion process. Forcing the pin down outputs
            # first (dummy) sign bit 15.
            self._cs.low()
            time.sleep_us(10)

            # Read temperature bits 14-3 from MAX6675.
            value = 0
            for i in range(12):
                # SCK should resemble clock signal and new SO value
                # is presented at falling edge
                self._cycle_sck()
                value += MAX6675._so.value() << (11 - i)

            # Read the TC Input pin to check if the input is open
            self._cycle_sck()
            self._error = MAX6675._so.value()

            # Read the last two bits to complete protocol
            for i in range(2):
                self._cycle_sck()

            # Finish protocol and start new measurement
            self._cs.high()
            self._last_measurement_start = time.ticks_ms()

            self._last_read_temp = value * 0.25

        return self._last_read_temp