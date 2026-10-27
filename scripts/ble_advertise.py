# Advertise a known BLE name so a host scanner can confirm the ESP32 TX path.
import bluetooth
import time

NAME = "ESP32-BLE-TEST"
adv = bytearray(b"\x02\x01\x06")  # flags: LE general discoverable
adv += bytes([len(NAME) + 1, 0x09]) + NAME.encode()

ble = bluetooth.BLE()
ble.active(True)
print("ADV_START", NAME, "len", len(adv))
ble.gap_advertise(200000, adv_data=bytes(adv))
time.sleep(25)
print("ADV_DONE")
