# BLE scan diagnostic: report IRQ constants and every event received.
import bluetooth
import time
import binascii

print("IRQ_SCAN_RESULT", getattr(bluetooth, "IRQ_SCAN_RESULT", None))
print("IRQ_SCAN_DONE", getattr(bluetooth, "IRQ_SCAN_DONE", None))

ble = bluetooth.BLE()
ble.active(True)
print("active", ble.active())
print("config", ble.config("mac"))

counts = {}
results = []


def on_event(event, data):
    counts[event] = counts.get(event, 0) + 1
    if event == 5:
        addr_type, addr, adv_type, rssi, adv_data = data
        mac = binascii.hexlify(bytes(addr), ":").decode()
        results.append((mac, addr_type, adv_type, rssi, bytes(adv_data).hex()))


ble.irq(on_event)

for label, interval, window, active in (("passive_100", 30000, 30000, False), ("active_100", 30000, 30000, True)):
    ble.gap_scan(8000, interval, window, active)
    time.sleep(9)
    ble.gap_scan(None)
    time.sleep(0.5)
    print("PASS", label, "events", counts, "results", len(results))

for r in results[:40]:
    print("DEV", r[0], "type=%d adv_type=%d rssi=%d data=%s" % (r[1], r[2], r[3], r[4]))
print("TOTAL", len(results))
