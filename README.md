# wifi player

Hardware documentation for the ESP32 board used in this project.

## Contents

- [doc/device-hardware-profile.md](doc/device-hardware-profile.md) — full hardware profile: silicon, flash, USB/serial interface, read-only security state, boot behavior and known limits.
- [doc/bluetooth-scan.md](doc/bluetooth-scan.md) — Bluetooth/BLE scan attempt on the ESP32: method, results, cross-checks and what remains unproven.
- `doc/chip-and-flash.txt` — captured `esptool flash-id` output.
- `doc/efuse-security.txt` — captured read-only eFuse summary (selection only, no key blocks).
- `doc/usb-properties.txt` — captured udev properties and device paths.
- `doc/ble-*.log`, `doc/wifi-scan-evidence.log` — raw serial output from the scan runs.
- `scripts/` — MicroPython scripts used for the BLE/Wi-Fi tests (run with `mpremote`).

## Summary

| Item | Value |
|---|---|
| Chip | ESP32-D0WD-V3, rev v3.1 |
| CPU | Dual core, rated 240 MHz |
| Crystal | 40 MHz |
| Flash | 4 MB |
| MAC | `24:dc:c3:cd:0f:48` (BLE: `24:dc:c3:cd:0f:4a`) |
| UART bridge | CH340 (`1a86:7523`) on `/dev/ttyUSB0` |
| Secure boot / flash encryption | Not enabled |
| Existing firmware | Arduino + LVGL sketch, boot reported "Setup done" |
| BLE | Advertises and is received; scan completes, 0 advertisers in range |
| Classic Bluetooth | Not testable from MicroPython |

Board model, PSRAM, display/touch and audio hardware are not yet verified — see the "Remaining unknowns" section of the profile.

## Reproducing the scan

Requires `esptool`/`espefuse` (5.6.0 used here) and read/write access to the serial port.

```sh
esptool --port /dev/ttyUSB0 --baud 115200 --no-stub flash-id
esptool --port /dev/ttyUSB0 --baud 115200 --no-stub read-flash-status
espefuse --chip esp32 --port /dev/ttyUSB0 --baud 115200 summary
udevadm info --query=property --name=/dev/ttyUSB0
```

Bluetooth tests need MicroPython flashed temporarily; see [doc/bluetooth-scan.md](doc/bluetooth-scan.md) for the full backup/flash/restore sequence. Otherwise these are read-only probes: do not run `erase-flash` or burn eFuses unless you intend to.
