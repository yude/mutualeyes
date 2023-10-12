import network
import config
import utime

import utils

def prepare_wifi():
    """
    Wi-Fi 接続を準備します。
    リファレンス: https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf
    """
    print("[Info] Tries to connect to {}".format(config.WIFI_SSID))

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    while not wlan.isconnected():
        pass

    if config.WIFI_USE_DHCP is False:
        wlan.ifconfig(
            (
                config.WIFI_STATIC_IP,
                config.WIFI_SUBNET_MASK,
                config.WIFI_DEFAULT_GATEWAY,
                config.WIFI_DNS,
            )
        )

    for _ in range(10):
        status = wlan.status()
        if wlan.status() < 0 or wlan.status() >= network.STAT_GOT_IP:
            break
        print(f"Waiting for Wi-Fi connection... (Status: {status})")
        utime.sleep(1)
    else:
        raise RuntimeError("Wi-Fi connection timed out.")

    wlan_status = wlan.status()

    if wlan_status != network.STAT_GOT_IP:
        raise RuntimeError(
            "Failed to establish Wi-Fi connection. (Status: {})".format(wlan_status)
        )

    print("Wi-Fi connection is ready! ifconfig:", wlan.ifconfig())
    print(utils.stringify_mac(wlan.config('mac')))

    return wlan
