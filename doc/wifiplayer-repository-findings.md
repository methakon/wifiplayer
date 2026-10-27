# WiFiPlayer — repository findings and USB-speaker feasibility

**Reviewed:** 2026-10-27 IST  
**Repository:** [methakon/wifiplayer](https://github.com/methakon/wifiplayer)  
**Baseline commit:** `e9de32e1a202e72645cb61462a046c6edfbe050c`  
**Status:** Desktop review and implementation feasibility study; **no USB speaker playback test performed**.

## Product requirement

Use the actual **ESP32-2432S028** 2.8-inch 240 × 320 LVGL touchscreen board as a Wi-Fi audio player/controller. The target **external speaker must receive audio via its USB port**. Bluetooth and the board's analog amplifier/passive-speaker connector are **not** part of the requested signal path. A USB connector that supplies only power is not a valid USB audio solution.

## Executive findings

1. The repository is a **hardware-scanning baseline**, not an audio firmware implementation. At the reviewed commit there is one README and four `doc/` evidence files. There is no tested player, build manifest, USB MSC/UAC stack, or implementation verification.
2. Direct probe evidence identifies **ESP32-D0WD-V3 rev 3.1**, rated dual-core 240 MHz, 40 MHz crystal, 4 MB flash, and a **CH340 USB-to-UART** bridge (`1a86:7523`, `ch341`, `/dev/ttyUSB0`). The factory Arduino/LVGL app reached `Setup done`. The board photo shows silkscreen `ESP32-2432S028` and both USB-C and Micro-USB connectors; routing of the second connector has not been electrically verified.
3. Original ESP32 has **no native USB OTG/full USB device peripheral** for standard USB Audio Class or USB Mass Storage emulation. A CH340 serial bridge cannot be turned into a UAC audio interface or flash-drive-emulating MSC device by an ESP32 firmware update.
4. The **speaker's USB role/protocol** is the primary unresolved design decision. A speaker's USB-A pen-drive port, a speaker that enumerates on a computer as a USB sound card, and a charging-only connector are fundamentally different.
5. An **ESP32-S3 USB-capable coprocessor** is a reasonable candidate, but only after matching the actual speaker's supported USB protocol. Supporting *any speaker with a USB port* is not technically guaranteed.

## 1. GitHub evidence ledger

| File | What it establishes | What it does not establish |
|---|---|---|
| [README.md](../README.md) | Project index, probe commands | Functional player design |
| [device-hardware-profile.md](device-hardware-profile.md) | Read-only chip, flash, boot, eFuse, USB state and caveats | Display/touch/audio/USB-audio functional testing |
| [chip-and-flash.txt](chip-and-flash.txt) | `esptool 5.6.0` actual chip and flash detection | Runtime speed, PSRAM presence |
| [efuse-security.txt](efuse-security.txt) | Secure boot and flash encryption inactive in selected eFuses | Comprehensive firmware security |
| [usb-properties.txt](usb-properties.txt) | CH340 VID/PID `1a86:7523`, driver `ch341`, device `/dev/ttyUSB0` | Native USB peripheral capability |

Raw facts from scans:

- Silicon: ESP32-D0WD-V3 rev v3.1, Wi-Fi and Bluetooth capable (Bluetooth **not** part of this project).
- CPU **rated** 240 MHz; operating frequency **not measured**.
- 4 MB SPI flash, 3.3 V flash selection; flash manufacturer ID `0x5e`, device `0x4016`. Exact manufacturer trade name unverified.
- CH340 interface USB 1.10, vendor-specific USB class; USB-UART serial, **not UAC**.
- Security: `FLASH_CRYPT_CNT=0`; `ABS_DONE_0=ABS_DONE_1=False`; no irreversible eFuse change made.
- Boot log: `Hello Arduino! V8.3.3`, `I am LVGL_Arduino`, `Setup done`. The version banner is not proof of installed library versions.
- Not measured: PSRAM, free heap, exact LVGL source, full board USB-C wiring, running peripheral pinout, actual Wi-Fi audio decoding, speaker USB interoperability.

The supplied photographs independently suggest the common Sunton/CYD model `ESP32-2432S028`; **do not infer** every GPIO assignment of `ESP32-2432S028R` or all dual-USB variants from one related schematic.

## 2. USB protocol and role matrix

| Observed external speaker function | Speaker USB role | Required adapter USB role | Consequence |
|---|---|---|---|
| Plays MP3s from ordinary thumb drive | **USB host**, MSC reader | **MSC device** emulating flash disk | Feasible for **stored/cached files**, not generic low-latency internet radio |
| Appears as playback sound device on Ubuntu/Windows | **USB UAC device** | **USB UAC host** sending PCM | True live decoded audio possible, subject to endpoint support |
| USB power/charging only | Neither audio role | None | No digital audio can be delivered on this connector |
| Proprietary implementation | Unknown | Vendor-specific | Requires exact device and protocol evidence |

**Direction matters:** “S3 as MSC host reading a pen drive” is the *opposite* of “S3 impersonates a pen drive for a speaker.” Similarly, “S3 UAC device acts as a USB sound card for a PC” is the *opposite* of “S3 host sends PCM to a USB audio speaker.”

## 3. Recommended candidate architectures

### A. Speaker acts as USB host / plays thumb-drive MP3s

```text
Wi-Fi / library / playlist services
             |
ESP32-2432S028: Wi-Fi + LVGL touchscreen controller
             | validated UART/SPI inter-controller commands
ESP32-S3: native USB Device + TinyUSB Mass Storage (MSC)
             | USB data; stable FAT volume presented to speaker
External speaker: USB HOST reads files and handles decoding/playback
```

Design constraints:

- Use a real, correctly powered **native USB** S3 connection, not a CH340 UART connector.
- Provide a FAT volume with stable file names, sectors and directory entries. Test FAT32 and the exact speaker's supported file extensions/bitrates.
- USB host can cache FAT tables, file size and directory state. **Writing the same filesystem from Wi-Fi while it is mounted externally is unsafe**; use a frozen snapshot and coordinated detach/re-enumeration or reliable single-owner storage strategy.
- A pseudo “endless MP3 file” is **not a universal stream**; many speaker firmwares stop at a known length, cache files or seek unpredictably. State live radio over MSC as *unproven*.
- There is no guarantee the speaker accepts a virtual/USB composite device even if a normal flash drive works.

### B. Speaker acts as a USB audio peripheral (UAC)

```text
Wi-Fi MP3/PCM -> jitter buffer -> codec -> PCM
                         |
             ESP32-S3 native USB HOST UAC OUT
                         |
               USB audio speaker (UAC DEVICE)
```

- This is the proper digital **live** audio route, but only for genuine USB sound devices.
- Confirm enumeration, UAC version, isochronous OUT endpoints, accepted formats/rates, full-speed compatibility, power/VBUS requirements and detach/recover behavior.
- Preserve the original LVGL board over an inter-controller serial link, or consider a new native-USB display board if integration cost becomes excessive.
- S3 native USB is **Full Speed 12 Mbit/s**, not high-speed 480 Mbit/s. Audio-rate claims must account for endpoint limits, not just raw link rate.

### C. Replace existing board with a USB-capable display board

An ESP32-S3-based display board could combine control and USB functions; this is a more substantial redesign and does **not** remove the requirement to identify whether the speaker expects MSC, UAC or charging-only USB.

## 4. Driver and reference inventory

| Component | Driver or source |
|---|---|
| Original ESP32 flash/debug | [Espressif esptool](https://github.com/espressif/esptool) |
| CH340 Linux serial | `ch341` kernel driver (already observed working) |
| UI | Existing LVGL demo, actual version/build still unverified |
| S3 native USB device | [ESP-IDF USB Device documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/usb_device.html) |
| MSC device stack | [Espressif USB device solutions](https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_overview/usb_device_solutions.html) |
| UAC host | [Espressif USB Host solutions](https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_overview/usb_host_solutions.html) |
| S3 USB host library | [ESP-USB USB Host](https://docs.espressif.com/projects/esp-usb/en/latest/esp32s3/usb_host.html) |
| Board reference | [ESP32-2432S028 PCB annotation](https://macsbug.wordpress.com/wp-content/uploads/2022/08/esp32_2432s028_pcb-3.pdf) |

**Do not assume** the presence of a USB-C receptacle grants OTG capability. Verify its D+/D- routing and bridge circuitry first. No firmware change can change the original ESP32 silicon's USB peripheral availability.

## 5. Non-destructive validation and release gates

1. **Preserve:** make a verified, hashed full 4 MB flash backup before writes; save existing partition map, UART boot log and board photos. No flash erase, eFuse burning or experimental wiring at this stage.
2. **Identify speaker:** document exact model/connector/manual. If USB-A thumb-drive input, test with a small conventional FAT32 drive holding ordinary MP3 tracks. If speaker is an external USB-audio device, enumerate on a Linux host and inspect `lsusb -v`, `aplay -l`, audio endpoint descriptors. **Never directly connect two USB host outputs.**
3. **Prove USB-only:** use a native USB ESP32-S3 test board in the **correct role**; play a known file (MSC) or known PCM test (UAC) through an actual speaker **with Bluetooth off**.
4. **Add network path:** bounded buffering, timeout and reconnection, file/playlist changes and explicit error states. For MSC, never expose simultaneously mutated FAT metadata to the speaker.
5. **Add LVGL:** separate display-thread ownership, queued commands, UI state machine, persistent settings and recovery.
6. **Acceptance:** log speaker protocol, voltage/current, successful USB audio playback, cold start, repeat reconnect/disconnect, no filesystem corruption, no Bluetooth audio route.

**Unresolved:** target speaker's protocol; native-USB coprocessor choice; dual-USB port electrical mapping; PSRAM; exact display/touch drivers; whether requirement includes **live** streaming or file-based playback.

**Conclusion:** This project is feasible for **defined speaker models and documented USB protocols**, but is **not** implementable as a universal USB-to-any-speaker Wi-Fi dongle on the unmodified original ESP32.
