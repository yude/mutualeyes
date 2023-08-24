import uasyncio
from sched.sched import schedule
import wifi
import machine
import httpd
import _thread
import node
import clock

wlan = 0
loop = uasyncio.get_event_loop()

async def routine():
    loop.create_task(schedule(node.check_node, 'every 5 secs', hrs=None, mins=None, secs=range(0, 60, 5)))

    while True:
        await uasyncio.sleep(1000)

if __name__ == '__main__':
    # ネットワークに接続
    # global wlan
    wlan = wifi.prepare_wifi()
    # 時刻を設定
    clock.set_clock()

    ## 起動メッセージ
    print("""\n
            __         __              __    _    \n
           / /______ _/ /______ ______/ /_  (_)___\n
          / //_/ __ `/ //_/ __ `/ ___/ __ \/ /_  /\n
         / ,< / /_/ / ,< / /_/ (__  ) / / / / / /_\n
        /_/|_|\__,_/_/|_|\__,_/____/_/ /_/_/ /___/\n
        \n
        Welcome to kakashiz,\n
        Decentralized monitoring system for\n
        microcomputers.\n
        \n
        Machine information:\n
        [Network]\n
         - Local IP address: {}\n
         - Wi-Fi SSID: {}\n
        \n
        [Clock]
         - Current RTC time: {}/{}/{} {}:{}:{}\n
        \n
    """.format(
        # Local IP address
        wlan[0],
        # Wi-Fi SSID
        wlan.config('ssid'),
        # Clock
        machine.RTC.datetime()[0],  # Year
        machine.RTC.datetime()[1],  # Month
        machine.RTC.datetime()[2],  # Day
        machine.RTC.datetime()[4],  # Hour
        machine.RTC.datetime()[5],  # Minute
        machine.RTC.datetime()[6],  # Sec
    ))

    # タスクを起動
    ## Web サーバ
    _thread.start_new_thread(httpd.run_httpd(wlan))
    ## 定時処理
    uasyncio.run(routine())
