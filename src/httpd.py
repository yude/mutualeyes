import json
import utils
import uuid

import event
import config

from nanoweb import HttpError, Nanoweb

app = Nanoweb(80)

@app.route('/')
async def _index(req):
    await return_ok('200 OK!')

@app.route('/event')
async def _event(req):
    try:
        content_length = int(req.headers['Content-Length'])
        content_type = req.headers['Content-Type']
    except KeyError:
        raise HttpError(req, 400, '"INVALID_JSON_FORMAT"}')

    if content_type != 'application/json':
        raise HttpError(req, 400, '"INVALID_JSON_FORMAT"}') 
    
    req_body = (await req.read(content_length)).decode()

    req_body = utils.auto_decode(req_body)
    if req_body is None:
        await return_ok(req, '{"result": "INVALID_JSON_FORMAT"}')
    try:
        req_json = json.loads(req_body)
    except ValueError:
        await return_ok(req, '{"result": "INVALID_JSON_FORMAT"}')

    query = event.query_to_event(req_json)
    if query is not None:  # クエリの解釈に成功した場合
        identified = event.identify_event(query)
        if identified is None:
            event.events[str(uuid.uuid4())] = query
        else:
            pass

        await return_ok(req, '{"result": "SUCCESS"}')
    else:
        await return_ok(req, '{"result": "FAIL_TO_RECORD_EVENT"}')

async def return_ok(req, body: str):
    await req.write("HTTP/1.1 200 OK\r\n\r\n")
    await req.write(body)