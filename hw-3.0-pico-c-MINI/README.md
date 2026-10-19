# Thermal Probe Alerter: Hardware v3.0 MINI (Pico C SDK)

Status: in planning. No code yet.

hw-3.0 MINI is a small, simple, single-probe monitor: one unit per thing you
want to watch. It will be a self-contained project, built with the Raspberry
Pi Pico C/C++ SDK. It will not share any files with `hw-1.0-pico-python/` or
`hw-2.0-pico-python/`.

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

## Why hw-3.0?

hw-2.0 grew to 8 probes, a buzzer, and more LEDs than the Pico has GPIO pins
for. See [`../hw-2.0-pico-python/README.md`](../hw-2.0-pico-python/README.md)
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
