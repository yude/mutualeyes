import json
import utils
import uuid
import utime
import random

import event
import config

from nanoweb import HttpError, Nanoweb


import http_client.core as http_client
import http_client.json_middleware as json_middleware

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

@app.route("/get-seed")
async def _get_seed(req):
    seed = str(random.getrandbits(32)) + str(random.getrandbits(32)) + str(random.getrandbits(32))
    await return_ok(req, seed)

    new_hash = await utils.get_auth_hash(seed)
    utils.hashes += [
        utils.AuthHash(
            new_hash,
            utime.time()
        )
    ]
    print(f"New hash: {new_hash}")
    
    return

@app.route("/notify-done")
async def _notify_done(req):
    # HTTP ヘッダーの確認
    try:
        content_length = int(req.headers["Content-Length"])
        content_type = req.headers["Content-Type"]
    except KeyError:
        raise HttpError(req, 400, '{"result": "BAD_REQUEST"}')

    if content_type != "application/json":
        raise HttpError(req, 400, '{"result": "BAD_REQUEST"}')
    

    # Body を読んで JSON として正しいか確認する
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
        auth_hash = req_json["hash"]
        auth_hash_ok = await utils.use_auth_hash(auth_hash)
        if not auth_hash_ok:
            if config.LOG_LEVEL == "ALL":
                utils.print_log("Received an invalid request regarding authentication.")
            return

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

async def return_json_ok(req, body: str):
    await req.write("HTTP/1.1 200 OK\r\n")
    await req.write("Content-Type: application/json\r\n\r\n")
    await req.write(body)
    await req.write('\r\n')

async def return_ok(req, body: str):
    await req.write("HTTP/1.1 200 OK\r\n")
    await req.write("Content-Type: text/plain\r\n\r\n")
    await req.write(body)
    await req.write('\r\n')
