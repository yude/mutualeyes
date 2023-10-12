import uasyncio
import urequests
import utime
import copy
import uuid
import http_client.core as http_client
import http_client.json_middleware as json_middleware

import utils
import config
import event
import constrants


class Node:
    def __init__(self, name: str, endpoint: str, status: str | None = None, down_count: int = 0):
        self.name = name
        self.endpoint = endpoint
        self.status = status
        self.down_count = down_count

    def __lt__(self, other):
        return self.name < other.name


async def check_node(target: Node) -> str | None:
    """
    入力されたノードに対して、稼働状況を確認する等の処理を行います。
    """

    if target.down_count is None:
        target.down_count = 0

    if target.name == utils.whoami():
        return None

    utils.print_log("[Monitor] Checking node {}...".format(target.name))

    res_dict = None

    try:
        while True:
            req_dict = {
                "url": target.endpoint,
                "headers": {
                    "Accept": "application/json"
                }
            }

            r = await json_middleware.wrap(http_client.request)
            res_dict = await uasyncio.wait_for_ms(r(req_dict), 2500)

            try:
                _ = res_dict['status']['code']
            except KeyError:
                pass
            else:
                break

    except uasyncio.TimeoutError:
        await down_node(target)
        return str(target.name)

    if res_dict['status']['code'] != 200:
        await down_node(target)
        return str(target.name) 

    if target.status == "NODE_DOWN":
        await recover_node(target)
        return str(target.name)

    if target.status is None or target.status == "NODE_UNKNOWN":
        target.status = "NODE_UP"

    utils.print_log("[Monitor] Node {} is up.".format(target.name))
    target.down_count = 0
    return str(target.name)

async def down_node(target: Node):
    if target.status == "NODE_DOWN":
        utils.print_log("[Monitor] Node {} is still down.".format(target.name))
        return

    if target.status != "NODE_DOWN":
        target.down_count = target.down_count + 1
        
    if target.down_count > 2 and target.status != "NODE_DOWN":
        utils.print_log("[Monitor] Node {} is down.".format(target.name))
        target.status = "NODE_DOWN"
        await register_event(target, "NODE_DOWN")
    else:
        utils.print_log("[Monitor] Node {} did not respond. (Confirmation stage: {} / 2)".format(target.name, target.down_count))

async def recover_node(target: Node):
    utils.print_log("[Monitor] Node {} is recovered.".format(target.name))
    target.status = "NODE_UP"
    target.down_count = 0
    await register_event(target, "NODE_UP")

async def check_node_parallel():
    """
    check_node() を uasyncio を使って非同期的に実行します。
    """
    while True:
        tasks = [check_node(node) for node in config.NODES]
        await uasyncio.gather(*tasks)
        await uasyncio.sleep(15)


async def register_event(node: Node, event_type: str):
    """
    イベントをノード内のイベント一覧に登録します。
    """

    # 新しくイベントを作成する
    new_event = event.Event(
        origin=copy.copy(node.name),
        created_on=utime.time(),
        type=event_type,
        status="WAIT_CONFIRM",
        source=utils.whoami(),
        worker_node=[utils.whoami()],
        confirmed_on=utime.time(),
    )

    # 重複していれば、そこで処理を終わる
    identified = event.identify_event(new_event)
    if identified is not None:
        return str(node.name)

    # 重複していなければ、登録する
    event.events[str(uuid.uuid1())] = new_event
