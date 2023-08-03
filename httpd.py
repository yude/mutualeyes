from microdot_asyncio import Microdot
import constrants

async def run_httpd(wlan):
    """
    Microdot を用いて http サーバーを起動します。
    主に、監視対象ノード間のコミュニケーションに使用されます。
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

    @app.post('/event/add')
    async def _event_add(req):
        return """
        Not implemented
        """

    app.run(
        host='0.0.0.0',
        port=constrants.HTTP_PORT,
        debug=True,
        ssl=None,
    )
