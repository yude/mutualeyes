import uasyncio
import schedule
import wifi
import httpd
import _thread
import node

wlan = 0

async def routine():
    # Wait for Wi-Fi preparation
    while True:
        if wlan != 0:
            break

    schedule.every(5).seconds.do(node.check_node)
    while True:
        schedule.run_pending()
        uasyncio.sleep(1)

async def run_httpd():
    global wlan
    wlan = await wifi.prepare_wifi()

if __name__ == '__main__':
    _thread.start_new_thread(routine)
    uasyncio.run(run_httpd())
