import network
import config
import utime

import utils

def prepare_wifi():
    """
    Wi-Fi 接続を準備します。
    リファレンス: https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf
    """
    print("[Info] Wi-Fi アクセスポイント {} に接続しようとしています ...".format(config.WIFI_SSID))

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
        print(f"Wi-Fi 接続を待機しています ... (状態: {status})")
        utime.sleep(1)
    else:
        raise RuntimeError("Wi-Fi アクセスポイントに接続できませんでした。")

    wlan_status = wlan.status()

    if wlan_status != network.STAT_GOT_IP:
        raise RuntimeError(
            "Wi-Fi アクセスポイントへの接続を確立できませんでした。 (状態: {})".format(wlan_status)
        )

    print("Wi-Fi アクセスポイントに接続しました。\nインターフェースの情報:", wlan.ifconfig())
    print(f"MAC アドレス: {utils.stringify_mac(wlan.config('mac'))}")

    return wlan
