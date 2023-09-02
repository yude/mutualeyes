import uasyncio
import urequests
import utime

import config
import event

class Node:
    def __init__(
            self,
            name: str,
            endpoint: str,
    ):
        self.name = name
        self.endpoint = endpoint


"""
check_node(node: Node)
入力されたノードに対して、稼働状況を確認する等の処理を行います。
"""
async def check_node(node: Node) -> str:
    print("Checking node {}...".format(node.name))

    try:
        res = urequests.get(node.endpoint)
        await uasyncio.sleep(2)
    except OSError as e:
        await register_event(node)
        return str(node.name)

    if res.status_code != 200:
        await register_event(node)
        return str(node.name)
    
    return str(node.name)

async def check_node_parallel():
    while True:
        print("Check node parallel.")
        tasks = [check_node(node) for node in config.NODES]
        await uasyncio.gather(*tasks)
        await uasyncio.sleep(5)

async def register_event(node: Node):
    print("[Check] Node {} is down.".format(node.name))
        # ダウンしているので、新しくイベントを作成する
        new_event = event.Event(
            origin=copy.copy(node.name),
            created_on=utime.time(),
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
