# Wi-Fi scan cross-check: proves the ESP32 RF front-end/antenna receives.
import network

sta = network.WLAN(network.STA_IF)
sta.active(True)
nets = sta.scan()
print("AP_COUNT", len(nets))
for n in sorted(nets, key=lambda x: -x[3]):
    ssid = n[0].decode("utf-8", "replace") if n[0] else ""
    print("AP ssid=%r bssid=%s ch=%d rssi=%d auth=%d hidden=%d" % (ssid, n[1], n[2], n[3], n[4], n[5]))
sta.active(False)
