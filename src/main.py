import uasyncio as asyncio
import machine
import httpd
import utime
import clock

import utils
import event
import node
import wifi
import config

wlan = 0

async def routine():
    while True:
        await node.check_node_parallel()
        await event.check_event_parallel()
        await asyncio.sleep(5)

def main():
    loop = asyncio.get_event_loop()
    loop.create_task(routine())
    loop.create_task(httpd.app.run())
    loop.run_forever()


if __name__ == "__main__":
    # ネットワークに接続
    wlan = wifi.prepare_wifi()

    # 自分のノードが特定できているかを確認
    if utils.whoami() is None:
        raise RuntimeError("Could not detect who am I.")

    # 時刻を設定
    clock.set_clock()
    rtc = machine.RTC()

    ## 起動メッセージ
    print(
        """
            __         __              __    _    
           / /______ _/ /______ ______/ /_  (_)___
          / //_/ __ `/ //_/ __ `/ ___/ __ \/ /_  /
         / ,< / /_/ / ,< / /_/ (__  ) / / / / / /_
        /_/|_|\__,_/_/|_|\__,_/____/_/ /_/_/ /___/

        Welcome to kakashiz running on {},
        Decentralized alive-monitoring system for
        microcomputers.

        Machine information:
        [Network]
         - Local IP address: {}
         - MAC address: {}
         - Wi-Fi SSID: {}
        [Clock]
         - Current RTC time: {}
    """.format(
            # Whoami
            utils.whoami(),
            # Local IP address
            wlan.ifconfig()[0],
            # MAC address
            utils.stringify_mac(wlan.config('mac')),
            # Wi-Fi SSID
            wlan.config("essid"),
            # Clock
            utils.format_epoch(utime.time())
        )
    )

    # タスクを起動
    main()
