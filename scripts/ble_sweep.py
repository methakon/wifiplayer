# Longer BLE sweep: catches intermittent advertisers (phones, beacons, earbuds).
import bluetooth
import time
import binascii

DURATION_MS = 45000

ble = bluetooth.BLE()
ble.active(True)

seen = {}
events = {}


def adv_fields(data):
    i = 0
    name = None
    uuids = []
    mfg = None
    while i < len(data):
        ln = data[i]
        if ln == 0 or i + 1 >= len(data):
            break
        typ = data[i + 1]
        payload = bytes(data[i + 2:i + 1 + ln])
        if typ in (0x08, 0x09):
            try:
                name = payload.decode("utf-8")
            except Exception:
                pass
        elif typ in (0x02, 0x03):
            uuids = [binascii.hexlify(payload).decode()]
        elif typ == 0xFF:
            mfg = binascii.hexlify(payload).decode()
        i += 1 + ln
    return name, uuids, mfg


def on_event(event, data):
    events[event] = events.get(event, 0) + 1
    if event == 5:
        addr_type, addr, adv_type, rssi, adv_data = data
        mac = binascii.hexlify(bytes(addr), ":").decode()
        nm, uu, mf = adv_fields(adv_data)
        if mac in seen:
            e = seen[mac]
            if rssi > e[1]:
                e[1] = rssi
            if nm and not e[2]:
                e[2] = nm
            e[3] += 1
        else:
            seen[mac] = [addr_type, rssi, nm, 1, uu, mf]


ble.irq(on_event)
ble.gap_scan(DURATION_MS, 30000, 30000, True)
time.sleep(DURATION_MS / 1000 + 2)
ble.gap_scan(None)
time.sleep(0.5)

print("SWEEP_MS=%d EVENTS=%s DEVICES=%d" % (DURATION_MS, events, len(seen)))
for mac, (atype, rssi, nm, cnt, uu, mf) in sorted(seen.items(), key=lambda kv: -kv[1][1]):
    print("DEV %s type=%d rssi=%d reports=%d name=%s" % (mac, atype, rssi, cnt, nm or "-"))
print("SCAN_DONE")
