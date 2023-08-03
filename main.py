import uasyncio
import wifi
import httpd

async def main():
    wlan = await wifi.prepare_wifi()

    await httpd.run_httpd(wlan)

if __name__ == '__main__':
    uasyncio.run(main())
