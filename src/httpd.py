import json
import utils
import uuid

import event
import config
import node

from nanoweb import HttpError, Nanoweb

app = Nanoweb(config.HTTP_PORT)


@app.route("/")
async def _index(req):
    await return_ok(req, "200 OK!")


@app.route("/event")
async def _event(req):
    try:
        content_length = int(req.headers["Content-Length"])
        content_type = req.headers["Content-Type"]
    except KeyError:
        raise HttpError(req, 400, '{"result": "BAD_REQUEST"}')

    if content_type != "application/json":
        raise HttpError(req, 400, '{"result": "BAD_REQUEST"}')

    req_body = (await req.read(content_length)).decode()

    if config.LOG_LEVEL == "ALL":
        utils.print_log("New request received for event sharing.")
        print("Request body: " + req_body)

    req_json = None
    if req_body is not None:
        try:
            req_json = json.loads(req_body)
        except ValueError:
            await return_json_ok(req, '{"result": "JSON_VALUE_ERROR"}')
            
            return

    if req_json is not None:
        query = event.query_to_event(req_body)
        if query is not None:  # クエリの解釈に成功した場合
            identified = await event.identify_event(query)

            if identified is None:
                event.events[str(uuid.uuid4())] = query
                await return_json_ok(req, '{"result": "SUCCESS_WITH_REGISTER"}')
            else:
                identified.worker_node.append(req_json["sent_from"])
                await return_json_ok(req, '{"result": "SUCCESS_WITH_ACKNOWLEDGE"}')

            return
        else:
            await return_json_ok(req, '{"result": "FAILED_TO_RECORD_EVENT"}')
            return
    
    await return_json_ok(req, '{"result": "FAILED_TO_DECODE_JSON"}')
    return

@app.route("/notify-done")
async def _notify_done(req):
    try:
        content_length = int(req.headers["Content-Length"])
        content_type = req.headers["Content-Type"]
    except KeyError:
        raise HttpError(req, 400, '{"result": "BAD_REQUEST"}')

    if content_type != "application/json":
        raise HttpError(req, 400, '{"result": "BAD_REQUEST"}')

    req_body = (await req.read(content_length)).decode()
    if config.LOG_LEVEL == "ALL":
        utils.print_log("New request received for syncing notification status.")
        print("Request body: " + req_body)

    req_json = None
    if req_body is not None:
        try:
            req_json = json.loads(req_body)
        except ValueError:
            await return_json_ok(req, '{"result": "JSON_VALUE_ERROR"}')

            return

    if req_json is not None:
        query = event.query_to_event(req_body)

        if query is not None:
            identified = await event.identify_event(query)
            if identified is None:
                await return_json_ok(req, '{"result": "UNKNOWN_EVENT"}')
            else:
                identified.status = "DELIVERED"
                await return_json_ok(req, '{"result": "SUCCESS"}')

            return
        else:
            await return_json_ok(req, '{"result": "FAILED_TO_DECODE_JSON"}')
            return

    await return_json_ok(req, '{"result": "FAILED_TO_DECODE_JSON"}')
    return

async def return_ok(req, body: str):
    await req.write("HTTP/1.1 200 OK\r\n\r\n")
    await req.write("Content-Type: text/plain\r\n\r\n")
    await req.write(body)


async def return_json_ok(req, body: str):
    await req.write("HTTP/1.1 200 OK\r\n\r\n")
    await req.write("Content-Type: application/json\r\n\r\n")
    await req.write(body)
