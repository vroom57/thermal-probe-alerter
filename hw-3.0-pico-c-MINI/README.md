# Thermal Probe Alerter: Hardware v3.0 MINI (Pico C SDK)

Status: in planning. No code yet.

hw-3.0 MINI is a small, simple, single-probe monitor: one unit per thing you
want to watch. It will be a self-contained project, built with the Raspberry
Pi Pico C/C++ SDK. It will not share any files with `hw-1.0-pico-python/` or
`hw-2.0-pico-python-MAXI/`.

## Planned design

- A single Pico W in a small box, powered over USB.
- One high-temp (Type K) and/or low-temp (DS18B20) probe.
- A buzzer for local alerts.
- Possibly a small display.
- WiFi for email alerts. Each unit has its own IP address.
- Need more probes? Use more units. The cases may clip together.
- Written in C: compiled, fast to boot, reliable, and cheap to build.

## Planned uses

One MINI per appliance:

- Fridges and freezers: alert when the temperature rises too high.
- Ovens (experimental): alert when the oven has been on longer than a set
  time, for example 4 hours.

## Temperature probes

Overall range: −55 °C (−67 °F) to 1,024 °C (1,875 °F), depending on the
probe used. Figures below are from the chip datasheets.

| | DS18B20 (low-temp) | Type K + MAX6675 board (high-temp) |
| :--- | :--- | :--- |
| **Range** | −55 to +125 °C (−67 to +257 °F) | 0 to +1024 °C (32 to ~1875 °F) |
| **Accuracy** | ±0.5 °C (±0.9 °F) from −10 to +85 °C, ±2 °C outside that | Roughly ±2–3 °C |
| **Resolution** | Up to 0.0625 °C | 0.25 °C |
| **Reads below freezing?** | Yes | **No** |

- **Fridges and freezers:** use the DS18B20. A freezer at about −18 °C
  (0 °F) is well within its range.
- **Ovens and diesel heater exhaust:** use the Type K. Ovens reach about
  260 °C (500 °F), past the DS18B20's 125 °C limit.
- The MAX6675 board cannot read below 0 °C (32 °F), even though a Type K
  thermocouple can. For Type K below freezing, a MAX31855 board covers about
  −200 to +1350 °C.

> [!IMPORTANT]
> This is an **uncalibrated** hobby unit. The real range and accuracy depend
> on the quality of the probes and boards you buy. Cheap waterproof DS18B20
> probes often have cable jackets rated well below 125 °C, and many Type K
> probes are only rated to about 400–600 °C. Check each part's listing, and
> compare readings against a known-good thermometer before trusting them.

## Why hw-3.0?

hw-2.0 grew to 8 probes, a buzzer, and more LEDs than the Pico has GPIO pins
for. See [`../hw-2.0-pico-python-MAXI/README.md`](../hw-2.0-pico-python-MAXI/README.md)
for the full story.

## License

Copyright (C) 2026 Virgil Mehalek

Licensed under the GNU General Public License v3.0 or later. See the
[LICENSE](LICENSE) file for the full text.

## Disclaimer

This is a personal hobby project, provided "as is" without warranty of any
kind. Use it at your own risk.

It is NOT designed, tested, or certified for life-safety, fire-protection,
medical, or other critical uses, and must not be relied on to protect people,
animals, or property. Temperature readings may be inaccurate, and alerts
(buzzer, display, and email) can be delayed or fail entirely because of
sensor, wiring, WiFi, power, or software faults.

Always use properly certified safety devices (smoke and CO detectors, thermal
cutoffs, etc.) for anything that matters. The author accepts no liability for
any damage, injury, or loss resulting from use of this code or hardware
design.
