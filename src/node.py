import uasyncio
import urequests
import utime
import copy
import uuid

import utils
import config
import event
import constrants


class Node:
    def __init__(self, name: str, endpoint: str, status: str | None = None):
        self.name = name
        self.endpoint = endpoint
        self.status = status


async def check_node(target: Node) -> str:
    """
    入力されたノードに対して、稼働状況を確認する等の処理を行います。
    """
    print("[Monitor] Checking node {}...".format(target.name))

    try:
        res = urequests.get(target.endpoint, timeout=constrants.HTTP_GET_TIMEOUT)
        await uasyncio.sleep(2)
    except OSError:
        if target.status != "NODE_DOWN":
            target.status = "NODE_DOWN"
            await register_event(target, "NODE_DOWN")
        return str(target.name)

    if res.status_code != 200:
        if target.status != "NODE_DOWN":
            target.status = "NODE_DOWN"
            await register_event(target, "NODE_DOWN")
        return str(target.name)

    if target.status is None or target.status == "NODE_UNKNOWN":
        target.status = "NODE_UP"

    if target.status == "NODE_DOWN":
        target.status = "NODE_UP"
        await register_event(target, "NODE_UP")
        return str(target.name)

    return str(target.name)


async def check_node_parallel():
    """
    check_node() を uasyncio を使って非同期的に実行します。
    """
    while True:
        tasks = [check_node(node) for node in config.NODES]
        await uasyncio.gather(*tasks)
        await uasyncio.sleep(5)


async def register_event(node: Node, event_type: str):
    """
    イベントをノード内のイベント一覧に登録します。
    """
    print(
        "[New event] Node {} is now {}.".format(
            node.name, utils.format_event_type(event_type)
        )
    )

    # 新しくイベントを作成する
    new_event = event.Event(
        origin=copy.copy(node.name),
        created_on=utime.time(),
        type=event_type,
        status="WAIT_CONFIRM",
        source=config.ME,
        worker_node=[config.ME],
        confirmed_on=None,
    )

    # 重複していれば、そこで処理を終わる
    identified = event.identify_event(new_event)
    if identified is not None:
        return str(node.name)

    # 重複していなければ、登録する
    event.events[str(uuid.uuid1())] = new_event
