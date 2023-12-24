import uasyncio as asyncio
import machine
import httpd
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
        raise RuntimeError("自分のノードを特定できません")

    # 時刻を設定
    clock.set_clock()
    rtc = machine.RTC()

    ## 起動メッセージ
    print(
        f"""
            __         __              __    _    
           / /______ _/ /______ ______/ /_  (_)___
          / //_/ __ `/ //_/ __ `/ ___/ __ \/ /_  /
         / ,< / /_/ / ,< / /_/ (__  ) / / / / / /_
        /_/|_|\__,_/_/|_|\__,_/____/_/ /_/_/ /___/

        情報:

        [一般]
         - ノード名: {utils.whoami()}
        [ネットワーク]
         - プライベート IP アドレス: {wlan.ifconfig()[0]}
         - MAC アドレス: {utils.stringify_mac(wlan.config('mac'))}
         - Wi-Fi アクセスポイント: {wlan.config("essid")}
        [時計]
         - RTC 時刻: {utils.format_epoch(clock.get_epoch())}
    """
    )

    # タスクを起動
    main()
