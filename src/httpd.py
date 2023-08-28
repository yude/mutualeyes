import json
import utils
import uuid

import event
import config

from noggin import Noggin, Response, HTTPError

app = Noggin()

async def run_httpd(wlan):
    """
    http サーバーを起動します。
    主に、監視対象ノード間のコミュニケーションに使用されます。
    """
    print("Starting httpd.")
    app.serve(port=80)

@app.route('/')
def _index(req):
    return "200 OK!"

@app.route('/event')
def _event(req):
    req_body = utils.auto_decode(req.body)
    if req_body is None:
        return Response("""
        {"result": "INVALID_JSON_FORMAT"}
        """,content_type='text/plain')
    try:
        req_json = json.loads(req_body)
    except ValueError:
        return Response("""
        {"result": "INVALID_JSON_FORMAT"}
        """,content_type='text/plain')

    query = event.query_to_event(req_json)
    if query is not None:  # クエリの解釈に成功した場合
        identified = event.identify_event(query)
        if identified is None:
            event.events[str(uuid.uuid4())] = query
        else:
            pass

        return Response("""
        {"result": "SUCCESS"}
        """,content_type='text/plain')
    else:
        return Response("""
        {"result": "FAIL_TO_RECORD_EVENT"}
        """,content_type='text/plain')
