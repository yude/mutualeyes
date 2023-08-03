import microdot_asyncio import Microdot

async def run_httpd(wlan):
    """
    Start http server using Microdot.
    https://microdot.readthedocs.io/en/latest/index.html
    """

    app = Microdot()

    # Routings
    @app.get('/')
    async def _index(req):
        return """
        200 OK!\n
        Local IP address: {local_ip_addr}\n
        """.format(
                local_ip_addr=wlan.ifconfig()[0]
            )
    