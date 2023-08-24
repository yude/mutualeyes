from http_server import MicroPyServer
import json
import utils
# import uuid

import event
import config

async def run_httpd(wlan):
    """
    http サーバーを起動します。
    主に、監視対象ノード間のコミュニケーションに使用されます。
    https://microdot.readthedocs.io/en/latest/index.html
    """

    app = MicroPyServer()

    # Routings
    app.add_route("/", route_root)
    app.add_route("/event", route_event)

    app.start()
    
def route_root():
    return """
        200 OK!\n
        """

def route_event():
    req_body = utils.auto_decode(req.body)
    if req_body is None:
        return """
        {"result": "INVALID_JSON_FORMAT"}
        """
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
