import uasyncio as asyncio
import wifi
import machine
import httpd
import _thread
from sched.sched import schedule
import node
import clock

wlan = 0

def main():
    loop = asyncio.get_event_loop()
    loop.create_task(node.check_node_parallel())
    loop.create_task(httpd.app.run())
    loop.run_forever()

if __name__ == '__main__':
    # ネットワークに接続
    wlan = wifi.prepare_wifi()
    # 時刻を設定
    clock.set_clock()

    rtc = machine.RTC()

    ## 起動メッセージ
    print("""
            __         __              __    _    
           / /______ _/ /______ ______/ /_  (_)___
          / //_/ __ `/ //_/ __ `/ ___/ __ \/ /_  /
         / ,< / /_/ / ,< / /_/ (__  ) / / / / / /_
        /_/|_|\__,_/_/|_|\__,_/____/_/ /_/_/ /___/

        Welcome to kakashiz,
        Decentralized monitoring system for
        microcomputers.

        Machine information:
        [Network]
         - Local IP address: {}
         - Wi-Fi SSID: {}
        [Clock]
         - Current RTC time: {}/{}/{} {}:{}:{}
    """.format(
        # Local IP address
        wlan.ifconfig()[0],
        # Wi-Fi SSID
        wlan.config('essid'),
        # Clock
        rtc.datetime()[0],  # Year
        rtc.datetime()[1],  # Month
        rtc.datetime()[2],  # Day
        rtc.datetime()[4],  # Hour
        rtc.datetime()[5],  # Minute
        rtc.datetime()[6],  # Sec
    ))

    # タスクを起動
    main()