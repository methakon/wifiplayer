# BLE scanner for ESP32 (MicroPython). Prints one line per unique advertiser.
import bluetooth
import time
import binascii

DURATION_MS = 15000

ble = bluetooth.BLE()
ble.active(True)

seen = {}


def adv_name(data):
    i = 0
    name = None
    while i < len(data):
        ln = data[i]
        if ln == 0 or i + 1 >= len(data):
            break
        typ = data[i + 1]
        if typ in (0x08, 0x09):
            try:
                name = bytes(data[i + 2:i + 1 + ln]).decode("utf-8")
            except Exception:
                name = None
        i += 1 + ln
    return name


def on_event(event, data):
    if event == 5:  # _IRQ_SCAN_RESULT
        addr_type, addr, adv_type, rssi, adv_data = data
        mac = binascii.hexlify(bytes(addr), ":")
        mac = mac.decode()
        nm = adv_name(adv_data)
        key = mac
        if key in seen:
            e = seen[key]
            if rssi > e[1]:
                e[1] = rssi
            if nm and not e[2]:
                e[2] = nm
            e[3] += 1
        else:
            seen[key] = [addr_type, rssi, nm, 1]


ble.irq(on_event)
print("SCAN_START duration_ms=%d" % DURATION_MS)
ble.gap_scan(DURATION_MS, 30000, 30000, True)
time.sleep(DURATION_MS / 1000 + 2)
ble.gap_scan(None)
time.sleep(0.5)

print("DEVICES=%d" % len(seen))
for mac, (atype, rssi, nm, cnt) in sorted(seen.items(), key=lambda kv: -kv[1][1]):
    print("DEV %s type=%d rssi=%d reports=%d name=%s" % (mac, atype, rssi, cnt, nm or "-"))
print("SCAN_DONE")
