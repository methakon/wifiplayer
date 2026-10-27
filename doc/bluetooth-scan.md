# Bluetooth scan on the ESP32

Date: 2026-10-27 (IST)
Device: ESP32-D0WD-V3 rev v3.1, 4 MB flash, CH340 UART (`/dev/ttyUSB0`)

## Result in one line

The ESP32 BLE stack works — it advertises and is received by a host scanner — and BLE scanning runs to completion without errors, but no advertising devices were detected in range during ~100 s of scanning in this environment.

## Method

The installed Arduino/LVGL firmware has no Bluetooth scanner, so a temporary MicroPython firmware was used and the original firmware was restored afterwards.

1. Full 4 MB flash backup before any change:
   `backup/original-flash-4mb.bin`, SHA-256 `28cc552e78e33db41fa58816cc28e2d04b01cb1458366f021a2e6750809acb5f`.
2. Erased flash and wrote MicroPython `ESP32_GENERIC-20260824-v1.29.0` at `0x1000`
   (SHA-256 `e67ad6015a0a504c1fec9aa9bbf589d0432ed28e62546f4f8dd8a147f8bd95f6`). The first write without erasing left a corrupted filesystem, hence the full erase.
3. Ran scan scripts over the serial REPL with `mpremote`.
4. Restored the original firmware: erase, write the 4 MB image at `0x0`, `esptool verify-flash` → "Verification successful (digest matched)".
5. Re-captured the boot log: identical to the pre-test capture (382 bytes, ending in `Hello Arduino! V8.3.3` / `I am LVGL_Arduino` / `Setup done`).

## Scan runs

| Run | Mode | Duration | Advertisers | IRQ events |
|---|---|---|---|---|
| `scripts/ble_scan.py` | passive, 100 % duty | 15 s | 0 | scan-done only |
| `scripts/ble_diag.py` | passive then active | 8 s + 8 s | 0 | scan-done only (1 + 2) |
| `scripts/ble_scan.py` (host trying to advertise) | active | 15 s | 0 | scan-done only |
| `scripts/ble_sweep.py` | active, 100 % duty | 45 s | 0 | `{6: 1}` |

Scan interval 30 ms, window 30 ms (100 % duty) in every run. `SCAN_DONE` (event 6) fired each time, so the scans were accepted and completed normally; event 5 (scan result) never fired. Raw output: `ble-scan-15s-1.log`, `ble-scan-diag.log`, `ble-scan-15s-host-advertising.log`, `ble-sweep-45s.log`.

## Cross-checks

- Host BLE scan through BlueZ/Bleak for 12 s found 0 devices as well, so the area is genuinely quiet rather than the ESP32 alone failing.
- Transmit path verified: with `scripts/ble_advertise.py` running, the host scanner received `ESP32-BLE-TEST` at `24:DC:C3:CD:0F:4A`, RSSI −81 dBm (`ble-advertise-test.log`). BLE MAC = base MAC …0F:48 + 2.
- RF receive path verified with Wi-Fi: `scripts/wifi_scan.py` found 2 APs (`Airtel_Dhar` −53 dBm, `kusankurdhar` −91 dBm), so the antenna and receiver front end work (`wifi-scan-evidence.log`).
- BlueZ advertising from the host (`bluetoothctl advertise on`) was attempted as the counter-test, but the CSR-based host adapter could not be confirmed to be transmitting; that run is therefore not evidence either way.

## What is still unproven

A BLE scan that receives a *known* advertiser has not been demonstrated. Everything above is consistent with a working scanner in an environment with nothing advertising, but it does not exclude an RX sensitivity problem. The −81 dBm TX reading at close range suggests a weak RF link, which is worth confirming.

Decisive test (needs a second device): put a phone 1–2 m from the ESP32, switch Bluetooth on and open the pairing/visibility screen so it advertises, then run `scripts/ble_sweep.py` again.

## Limits of this approach

- MicroPython on ESP32 exposes BLE only. Classic Bluetooth (older headsets, speakers, car kits, game controllers) cannot be discovered from this firmware; that needs the ESP-IDF BT discovery example or the Arduino `BluetoothSerial` API.
- While MicroPython was flashed, the LVGL application was inactive. It is now restored and verified.
- No Wi-Fi credentials, no flash contents and no eFuse values were published; only the summary above.
