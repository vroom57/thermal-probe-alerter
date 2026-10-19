# Pico W MicroPython Project Rules

**Status:** On hold at the Alpha (breadboard prototype) stage. The code runs on the breadboard, but the project is not under active development. New work is going to `../hw-3.0-pico-c-MINI/`.

## Environment Context
- **Hardware:** Raspberry Pi Pico W (RP2040) Gen 1. Not tested with Gen 2, but "should" work.
- **Runtime:** MicroPython (latest stable).
- **Upload Method:** User manually uploads via Thonny on Windows to Pico or another means to manually upload all python files into root of pico-w.
- **Config settings:** WiFi, email, and SMTP settings go in config.py. Temp settings and feature switches (EMAIL_ENABLED, SOUND_ENABLED, WATCHDOG_ENABLED, KEEPALIVE_ENABLED) go into main.py towards the top.


## Coding Standards
- Use **MicroPython-specific libraries** only (e.g., `machine`, `network`, `utime`, `uasyncio`, `umqtt.simple`).
- **NO standard Python libraries** like `requests`, `time`, or `threading` unless the MicroPython equivalent (e.g., `u` prefix) is used.
- **Onboard LED:** Use `machine.Pin("LED", machine.Pin.OUT)` for Pico W.
- **Memory Management:** Use `gc.collect()` in loops for long-running scripts to avoid fragmentation.

## Build & Test Commands
- **Check Syntax:** `python3 -m py_compile %f` (Runs inside the VM to catch basic typos).
- **Note:** Claude cannot run the code on the hardware. After edits, ask the user to "Run in Thonny" to verify hardware behavior.

## Hardware Wiring Map

Pin assignments below match the working `main.py` and `schematic-hw2.0.jpg`. Hardware v2.0 builds on v1.0, but the Type K wiring changed to a shared bus.

### Core Components
- **MCU:** Raspberry Pi Pico W (Pico1)
- **Display:** LCD2004 (20x4) via I2C (SDA: GP0/Pin 1, SCL: GP1/Pin 2), address 0x27 (39)
- **Buzzer:** 5V Active Buzzer (BUZ) via 2N2222 Transistor (Base: GP27/Pin 32 via 10k resistor R2)

### Temperature Sensors
- **High Temp (Type K):** Four MAX6675 boards on a shared bus
  - **Shared:** SCK: GP2, SO: GP4
  - **TK1 Right In (TempK_1_RightIn):** CS: GP6
  - **TK2 Left In (TempK_2_LeftIn):** CS: GP3
  - **TK3 Right Out (TempK_3_RightOut):** CS: GP8
  - **TK4 Left Out (TempK_4_LeftOut):** CS: GP9
- **Low Temp (Digital):** DS18B20 Probes (TempLow1-4). The LCD code expects four.
  - **Data Line:** All connected to GP10/Pin 14 with a 4.7k pull-up resistor (R1)

### LED Array (Visual Indicators)
Bottom rows: TK1 drives the right side, TK2 drives the left side. Top row (5 LEDs, left to right R/Y/G/Y/R): center Green shows WiFi, top-right Yellow and Red show TK3. Top-left Red (GP11) and Yellow (GP12) are wired but not used by `main.py` yet. Note: `main.py` still names GP12 `gpio_LED_Blu_Top` from hardware v1.0; it is the top-left Yellow LED.

**Resistor values are approximate.** Each LED's resistor was hand-tuned for even relative brightness across the array. Treat the values below as nominal, not exact, and don't "correct" them to standard values.

| Pin | Label | Color | Description | Resistor |
| :--- | :--- | :--- | :--- | :--- |
| **GP11** | D1 | Red | Top Left (not used yet) | 37Ω (R3) |
| **GP12** | D2 | Yellow | Top Left (not used yet) | 68Ω (R4) |
| **GP13** | D3 | Green | Top Center (WiFi status) | 260Ω (R5) |
| **GP14** | D4 | Yellow | Top Right (TK3 low/med) | 68Ω (R6) |
| **GP15** | D5 | Red | Top Right (TK3 high) | 37Ω (R7) |
| **GP16** | D6 | Blue | Right Bottom (TK1) | 46Ω (R8) |
| **GP17** | D7 | Green | Right Bottom (TK1) | 260Ω (R9) |
| **GP18** | D8 | Yellow | Right Bottom (TK1) | 68Ω (R10) |
| **GP19** | D9 | Red | Right Bottom (TK1) | 37Ω (R11) |
| **GP20** | D10 | Red | Left Bottom (TK2) | 37Ω (R12) |
| **GP21** | D11 | Yellow | Left Bottom (TK2) | 68Ω (R13) |
| **GP22** | D12 | Green | Left Bottom (TK2) | 260Ω (R14) |
| **GP26** | D13 | Blue | Left Bottom (TK2) | 46Ω (R15) |
