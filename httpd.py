from microdot_asyncio import Microdot
import json
import utils
import uuid

import event
import config

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

    @app.post('/event')
    async def _event_post(req):
        req_body = utils.auto_decode(req.body)
        try:
            req_json = json.loads(req_body)
        except ValueError:
            return """
            {"result": "INVALID_JSON_FORMAT"}
            """
        
        query = await event.query_to_event(req_json)
        if query is not None:  # クエリの解釈に成功した場合
            identified = await event.identify_event(query)
            if identified is None:
                event.events[str(uuid.uuid1())] = query
            else:
                pass

            return """
            {"result": "SUCCESS"}
            """
        else:
            return """
            {"result": "FAIL_TO_RECORD_EVENT"}
            """
    
    app.run(
        host='0.0.0.0',
        port=config.HTTP_PORT,
        debug=True,
        ssl=None,
    )
