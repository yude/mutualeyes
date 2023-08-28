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
    return "200 OK"

@app.route('/event', methods=['POST'])
def _event(req):
    req_body = utils.auto_decode(req.content)
    if req_body is None:
        return '{"result": "INVALID_JSON_FORMAT"}'
    try:
        req_json = json.loads(req_body)
    except ValueError:
        return '{"result": "INVALID_JSON_FORMAT"}'

    query = event.query_to_event(req_json)
    if query is not None:  # クエリの解釈に成功した場合
        identified = event.identify_event(query)
        if identified is None:
            event.events[str(uuid.uuid4())] = query
        else:
            pass

        return '{"result": "SUCCESS"}'
    else:
        return '{"result": "FAIL_TO_RECORD_EVENT"}'
