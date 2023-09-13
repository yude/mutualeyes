import uasyncio
import urequests
import utime
import copy
import uuid

import utils
import config
import event
import constrants

NodeStatus = utils.enum(UP=1, DOWN=2, UNKNOWN=3)


class Node:
    def __init__(self, name: str, endpoint: str, status: NodeStatus | None = None):
        self.name = name
        self.endpoint = endpoint
        self.status = status


"""
check_node(node: Node)
入力されたノードに対して、稼働状況を確認する等の処理を行います。
"""


async def check_node(target: Node) -> str:
    print("[Monitor] Checking node {}...".format(target.name))

    try:
        res = urequests.get(target.endpoint, timeout=constrants.HTTP_GET_TIMEOUT)
        await uasyncio.sleep(2)
    except OSError as e:
        if target.status != NodeStatus.DOWN:
            target.status = NodeStatus.DOWN
            await register_event(target, event.EventType.DOWN)
        return str(target.name)

    if res.status_code != 200:
        if target.status != NodeStatus.DOWN:
            target.status = NodeStatus.DOWN
            await register_event(target, event.EventType.DOWN)
        return str(target.name)

    if target.status == None or target.status == NodeStatus.UNKNOWN:
        target.status = NodeStatus.UP

    if target.status == NodeStatus.DOWN:
        target.status = NodeStatus.UP
        await register_event(target, event.EventType.UP)
        return str(target.name)

    return str(target.name)


async def check_node_parallel():
    while True:
        tasks = [check_node(node) for node in config.NODES]
        await uasyncio.gather(*tasks)
        await uasyncio.sleep(5)


async def register_event(node: Node, event_type: event.EventType):
    print(
        "[Monitor] Node {} is now {}.".format(
            node.name,
        )
    )
    # ダウンしているので、新しくイベントを作成する
    new_event = event.Event(
        origin=copy.copy(node.name),
        created_on=utime.time(),
        type=event.EventType.DOWN,
        status=event.EventStatus.WAIT_CONFIRM,
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
