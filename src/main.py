import uasyncio
from sched.sched import schedule
import wifi
import httpd
import _thread
import node

wlan = 0
loop = uasyncio.get_event_loop()

async def routine():
    global loop, wlan

    # Wait for Wi-Fi preparation
    while True:
        if wlan != 0:
            break
        uasyncio.sleep(1)

    loop.create_task(schedule(node.check_node, 'every 5 secs', hrs=None, mins=None, secs=range(0, 60, 5)))

    while True:
        await uasyncio.sleep(1000)

def run_httpd():
    global wlan
    wlan = wifi.prepare_wifi()

    httpd.run_httpd(wlan)

if __name__ == '__main__':
    _thread.start_new_thread(run_httpd())
    uasyncio.run(routine())
