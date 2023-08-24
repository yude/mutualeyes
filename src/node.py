import uasyncio
import urequests
# import datetime
# import copy
# import uuid

import config
import event

class Node:
    def __init__(
            self,
            name: str,
            endpoint: str,
    ):
        self.name = name,
        self.endpoint = endpoint


"""
check_node(node: Node)
入力されたノードに対して、稼働状況を確認する等の処理を行います。
"""
async def check_node(node: Node) -> str:
    res = urequests.get(node.endpoint)

    if res.status_code != 200:
        # ダウンしているので、新しくイベントを作成する
        new_event = event.Event(
            origin=copy.copy(node.name),
            created_on=datetime.datetime.now(),
            type=event.EventType.DOWN,
            status=event.EventStatus.WAIT_CONFIRM,
            source=config.ME,
            worker_node=[config.ME],
            confirmed_on=None
        )

        # 重複していれば、そこで処理を終わる
        identified = event.identify_event(new_event)
        if identified is not None:
            return str(node.name)

        # 重複していなければ、登録する
        event.events[str(uuid.uuid1())] = new_event

    return str(node.name)

# Lock for check_node_parallel()
check_node_lock = False

async def check_node_parallel():
    global check_node_lock
    if check_node_lock:
        return

    check_node_lock = True

    for f in uasyncio.as_completed([
        check_node(node)
        for node in config.NODES
    ]):
        finished_node = await f

        print(
            "[Check nodes] Periodical check of node {} is finished.".
            format(finished_node)
        )

    check_node_lock = False

    return
