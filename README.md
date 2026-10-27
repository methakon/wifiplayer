# wifi player

Hardware documentation for the ESP32 board used in this project.

## Contents

- [doc/device-hardware-profile.md](doc/device-hardware-profile.md) — full hardware profile: silicon, flash, USB/serial interface, read-only security state, boot behavior and known limits.
- `doc/chip-and-flash.txt` — captured `esptool flash-id` output.
- `doc/efuse-security.txt` — captured read-only eFuse summary (selection only, no key blocks).
- `doc/usb-properties.txt` — captured udev properties and device paths.

## Summary

| Item | Value |
|---|---|
| Chip | ESP32-D0WD-V3, rev v3.1 |
| CPU | Dual core, rated 240 MHz |
| Crystal | 40 MHz |
| Flash | 4 MB |
| MAC | `24:dc:c3:cd:0f:48` |
| UART bridge | CH340 (`1a86:7523`) on `/dev/ttyUSB0` |
| Secure boot / flash encryption | Not enabled |
| Existing firmware | Arduino + LVGL sketch, boot reported "Setup done" |

Board model, PSRAM, display/touch and audio hardware are not yet verified — see the "Remaining unknowns" section of the profile.

## Reproducing the scan

Requires `esptool`/`espefuse` (5.6.0 used here) and read/write access to the serial port.

```sh
esptool --port /dev/ttyUSB0 --baud 115200 --no-stub flash-id
esptool --port /dev/ttyUSB0 --baud 115200 --no-stub read-flash-status
espefuse --chip esp32 --port /dev/ttyUSB0 --baud 115200 summary
udevadm info --query=property --name=/dev/ttyUSB0
```

Read-only probes. Do not run `erase-flash` or burn eFuses unless you intend to.
