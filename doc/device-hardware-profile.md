# USB-connected ESP hardware profile

Project: wifi player
Scan date: 2026-10-27 (IST)
Status: USB, chip, flash, selected security eFuses and application boot verified on actual hardware. Remaining physical-board and peripheral details are explicitly unverified.

## Verified silicon and storage

| Property | Observed value |
|---|---|
| Chip | Espressif ESP32-D0WD-V3 |
| Silicon revision | v3.1 |
| CPU | Dual core, rated 240 MHz; low-power core also reported |
| Radio capabilities | Wi-Fi and Bluetooth |
| Crystal | 40 MHz |
| Base MAC | `24:dc:c3:cd:0f:48` |
| Chip ID | ESP32 has no separate chip ID according to esptool; MAC returned instead |
| Calibration | Vref calibration in eFuse |
| eFuse coding scheme | None |
| SPI flash manufacturer ID | `0x5e` (numeric ID verified; vendor name not independently verified) |
| SPI flash device ID | `0x4016` |
| Detected SPI flash capacity | 4 MB |
| Flash voltage | 3.3 V, selected by strapping pin |
| Flash status register | `0x0000` |

240 MHz is the chip's rated capability, not a measurement of the running firmware's CPU frequency. No PSRAM or total/free SRAM measurement was performed.

## Verified USB and serial interface

| Property | Observed value |
|---|---|
| USB bridge | QinHeng Electronics CH340 serial converter |
| USB VID:PID | `1a86:7523` |
| Product string | `USB Serial` |
| USB device revision | `2.64` (`ID_REVISION=0264`) |
| USB specification descriptor | USB 1.10 |
| Connection at initial scan | Bus 002, device 059; topology `2-1` |
| Kernel driver | `ch341` |
| Serial device | `/dev/ttyUSB0` |
| Tested UART speed | 115200 baud |
| By-ID path | `/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0` |
| By-path | `/dev/serial/by-path/pci-0000:00:14.0-usb-0:1:1.0-port0` |
| USB manufacturer string | Not supplied (`iManufacturer=0`) |
| Unique USB serial string | Not supplied (`iSerial=0`) |
| USB class | Vendor-specific, `0xff` |
| Interface subclass/protocol | `0x01` / `0x02` |
| Power descriptor | Bus-powered; declared maximum 98 mA |
| Configuration/interface count | One configuration, one interface |
| Endpoints | Bulk IN `0x82`, bulk OUT `0x02`, interrupt IN `0x81` |
| Bulk maximum packet size | 32 bytes per endpoint |
| Interrupt endpoint | 8-byte maximum packet, interval 1 |

The power descriptor is not a measured current draw or a board power limit. The CH340 identifies the USB-to-UART bridge, not the board model. The by-ID path is not unique because the bridge supplies no unique serial number. USB bus/device numbers may change on reconnection.

## Read-only security assessment

Selected eFuses were read using `espefuse summary`; no eFuses were programmed.

| Field | Value | Interpretation |
|---|---|---|
| `FLASH_CRYPT_CNT` | 0 | Hardware flash encryption not enabled |
| `ABS_DONE_0` | False | Secure boot V1 not enabled |
| `ABS_DONE_1` | False | Secure boot V2 not enabled |
| `JTAG_DISABLE` | False | JTAG not disabled by this eFuse; electrical access untested |
| `DISABLE_DL_ENCRYPT` | False | UART bootloader encryption function not disabled by this eFuse |
| `DISABLE_DL_DECRYPT` | False | UART bootloader decryption function not disabled by this eFuse |
| `DISABLE_DL_CACHE` | False | UART bootloader flash cache not disabled by this eFuse |
| `DISABLE_APP_CPU` | False | Second application CPU not disabled |
| `DISABLE_BT` | False | Bluetooth not disabled |
| `CHIP_CPU_FREQ_RATED` | True | CPU frequency rating recorded |
| `CHIP_CPU_FREQ_LOW` | False | Rated 240 MHz rather than 160 MHz |

`esptool get-security-info` returned `This command (0x14) is not supported in the current download mode`; the security conclusions above instead come from the successful selected eFuse read. No secret key blocks were requested or saved. These checks are not a full firmware security audit.

## Existing firmware and boot behavior

A five-second UART capture at 115200 baud, following an RTS reset, yielded 382 bytes. Relevant lines:

```text
ets Jul 29 2019 12:21:46
rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
configsip: 0, SPIWP:0xee
clk_drv:0x00,q_drv:0x00,d_drv:0x00,cs0_drv:0x00,hd_drv:0x00,wp_drv:0x00
mode:DOUT, clock div:2
load:0x3fff0018,len:4
load:0x3fff001c,len:1044
load:0x40078000,len:10124
load:0x40080400,len:5856
entry 0x400806a8
Hello Arduino! V8.3.3
I am LVGL_Arduino
Setup done
```

The device boots from SPI flash, uses DOUT in this boot log and reaches the application's `Setup done` message. The banner suggests an Arduino/LVGL application; `V8.3.3` is only a printed banner and is not independently verified as the installed library/SDK version. The 2019 ROM banner is not the firmware build date. No panic or reset loop appeared during this short capture; longer-term stability was not tested. Display, touch, audio, Wi-Fi connectivity and Bluetooth operation were not exercised.

## Evidence and repeatable probes

Saved command output:

- `chip-and-flash.txt`: successful chip identification and flash-ID probe.
- `efuse-security.txt`: selected read-only eFuse summary (no key blocks).
- `usb-properties.txt`: udev properties and device paths.

Commands used:

```sh
uv tool run --from esptool esptool --port /dev/ttyUSB0 --baud 115200 --no-stub flash-id
uv tool run --from esptool esptool --port /dev/ttyUSB0 --baud 115200 --no-stub chip-id
uv tool run --from esptool esptool --port /dev/ttyUSB0 --baud 115200 --no-stub read-flash-status
uv tool run --from esptool espefuse --chip esp32 --port /dev/ttyUSB0 --baud 115200 summary FLASH_CRYPT_CNT ABS_DONE_0 ABS_DONE_1 JTAG_DISABLE DISABLE_DL_ENCRYPT DISABLE_DL_DECRYPT DISABLE_DL_CACHE CHIP_VER_REV1 CHIP_VER_REV2 DISABLE_APP_CPU DISABLE_BT CHIP_CPU_FREQ_RATED CHIP_CPU_FREQ_LOW
udevadm info --query=property --name=/dev/ttyUSB0
```

Tool version: esptool/espefuse 5.6.0. UART capture used pyserial. Chip/flash commands used the ROM bootloader with `--no-stub`.

## Access history and safety

The initial scan was blocked by `[Errno 13] Permission denied` on `/dev/ttyUSB0`; the account lacked dialout membership. On continuation, explicit read/write checks both returned true and direct hardware probes succeeded. The exact operator-side permission change was not inspected. No system permissions or group memberships were changed by the agent.

The chip was reset during bootloader probes and the final UART capture. After the final reset, the existing application reached `Setup done`. No firmware was flashed or erased, no persistent device configuration or eFuses were modified, and no full flash dump was taken.

## Remaining unknowns / limits

- Physical development-board/module manufacturer and model, PCB revision, connector layout and pinout.
- PSRAM presence/capacity; usable/free SRAM and application memory usage.
- Flash vendor trade name and exact flash part number beyond numeric IDs.
- Display controller, resolution, touch controller, SD slot, audio hardware, and other peripherals.
- Actual firmware build identity, SDK version, partition layout and configured CPU frequency.
- Measured power consumption, electrical condition and peripheral functionality.

A photograph of both sides and module/PCB markings can help identify the physical board. Firmware-assisted diagnostics or a board schematic are needed for a fuller peripheral and memory inventory. Existing firmware and hardware have been preserved.

## Board identity: reported but not verified here

A desktop review in [wifiplayer-repository-findings.md](wifiplayer-repository-findings.md) reports a board photo with silkscreen `ESP32-2432S028` (2.8-inch 240x320 LVGL touch board, USB-C plus Micro-USB). That review is a document/photo study; this profile was produced from live probes of the attached device only, so the model is **reported, not device-verified**. Nothing in the chip-level data above contradicts it: ESP32-D0WD-V3, 4 MB flash and a CH340 bridge are all consistent with that board class.

That model is commonly sold with **no PSRAM**, an SPI display (ST7789 or ILI9341 depending on batch), a resistive XPT2046 touch controller and a small on-board speaker header. Each of those is a per-batch property and must be confirmed on this unit, not assumed.

Cheapest way to convert each unknown into evidence:

| Unknown | How to verify without guessing |
|---|---|
| PSRAM present / size | Flash a MicroPython `ESP32_GENERIC-SPIRAM` build and read the reported PSRAM size; a non-SPIRAM build boots either way, so absence of a size is weak evidence unless the SPIRAM build is used |
| Display controller and resolution | Run an LVGL/ST7789 or ILI9341 driver init over the board's SPI pins and look for correct orientation and colour test pattern on the panel |
| Touch controller | Read XPT2046 raw coordinates while pressing the panel; confirm they track the touch position |
| Audio | Trace the speaker header and amplifier markings against the schematic, then play a tone and confirm audible output |
| Board model / revision | Photograph both PCB sides; read the silkscreen and any module label |

No firmware, Wi-Fi credentials or flash contents are published here; the full 4 MB flash image stays local.
