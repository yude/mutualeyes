import rp2
import uasyncio
import network
import constrants

async def prepare_wifi():
    """
    The preparation of Wi-Fi connection.
    Reference: https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf
    """

    # Set country code
    rp2.country(constrants.WIFI_COUNTRY_CODE)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    wlan.connect(constrants.WIFI_SSID, constrants.WIFI_PASSWORD)

    for i in range(10):
        status = wlan.status()
        if wlan.status() < 0 or wlan.status() >= network.STAT_GOT_IP:
            break
        print(f'Waiting for Wi-Fi connection... (Status: {status})')
        uasyncio.sleep(1)
    else:
        raise RuntimeError('Wi-Fi connection timed out.')

    wlan_status = wlan.status()

    if wlan_status != network.STAT_GOT_IP:
        raise RuntimeError(
            'Failed to establish Wi-Fi connection. (Status: {})'.format(wlan_status))

    print('Wi-Fi connection is ready! ifconfig:', wlan.ifconfig())
    
    return wlan
