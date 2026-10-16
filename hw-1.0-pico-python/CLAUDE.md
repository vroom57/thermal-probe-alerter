# Pico W MicroPython Project Rules

## Environment Context
- **Hardware:** Raspberry Pi Pico W (RP2040) Gen 1. Not tested with Gen 2, but "should" work.
- **Runtime:** MicroPython (latest stable) Tested with v1.22.2
- **Upload Method:** User manually uploads via Thonny on Windows to Pico or another means to manually upload all python files into root of pico-w.
- **Config settings: ** For wi-fi and email passwords go in configy.py. Temp settings go into main.py towards the top.


## Coding Standards
- Use **MicroPython-specific libraries** only (e.g., `machine`, `network`, `utime`, `uasyncio`, `umqtt.simple`).
- **NO standard Python libraries** like `requests`, `time`, or `threading` unless the MicroPython equivalent (e.g., `u` prefix) is used.
- **Onboard LED:** Use `machine.Pin("LED", machine.Pin.OUT)` for Pico W.
- **Memory Management:** Use `gc.collect()` in loops for long-running scripts to avoid fragmentation.

## Build & Test Commands
- **Check Syntax:** `python3 -m py_compile %f` (Runs inside the VM to catch basic typos).
- **Note:** Claude cannot run the code on the hardware. After edits, ask the user to "Run in Thonny" to verify hardware behavior.

## Hardware Wiring Map

### Core Components
- **MCU:** Raspberry Pi Pico W (Pico1) 
- **Display:** LCD1602 (Disp1) via I2C (SDA: GP0/Pin 1, SCL: GP1/Pin 2) 
- **Buzzer (FUTURE, tested but not in hardware v1.0 / not used by main.py):** 5V Active Buzzer (BUZ) via 2N2222 Transistor (Base: GP27/Pin 32 via 10k resistor)

### Temperature Sensors
- **High Temp (Type K):** Two MAX6675 boards
  - **Left (TempKLeft):** SCK: GP5, CS: GP6, SO: GP7
  - **Right (TempKRight):** SCK: GP2, CS: GP3, SO: GP4
- **Low Temp (Digital) (FUTURE, not in hardware v1.0 / not used by main.py):** Three DS18B20 Probes (TempLow1, 2, 3)
  - **Data Line:** All connected to GP10/Pin 14 with a 4.7k pull-up resistor (R1)

### LED Array (Visual Indicators)
Hardware v1.0: 4 top LEDs (GP12–GP15). D1 (Red, GP11, R3 37Ω) and the 5-LED top layout (R/Y/G/Y/R) are a future hardware design, used only by `Test_Code/TEST_led_chase.py`.

**Resistor values are approximate.** Each LED's resistor was hand-tuned for even relative brightness across the array. A small trim pot per LED would be ideal, but hardware v1.0 design constraints didn't allow it. Treat the values below as nominal, not exact, and don't "correct" them to standard values.

| Pin | Label | Color | Description | Resistor |
| :--- | :--- | :--- | :--- | :--- |
| **GP12** | D2 | Blue | Top | 46Ω (R4) |
| **GP13** | D3 | Green | Top (WiFi status) | 260Ω (R5) |
| **GP14** | D4 | Yellow | Top | 68Ω (R6) |
| **GP15** | D5 | Red | Top (WiFi down) | 37Ω (R7) |
| **GP16** | D6 | Blue | Right Bottom | 46Ω (R8) |
| **GP17** | D7 | Green | Right Bottom | 260Ω (R9) |
| **GP18** | D8 | Yellow | Right Bottom | 68Ω (R10) |
| **GP19** | D9 | Red | Right Bottom | 37Ω (R11) |
| **GP20** | D10 | Red | Left Bottom | 37Ω (R12) |
| **GP21** | D11 | Yellow | Left Bottom | 68Ω (R13) |
| **GP22** | D12 | Green | Left Bottom | 260Ω (R14) |
| **GP26** | D13 | Blue | Left Bottom | 46Ω (R15) |