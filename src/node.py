import uasyncio
import clock
import copy
import uuid
import http_client.core as http_client
import http_client.json_middleware as json_middleware

import utils
import config
import event


class Node:
    """
    自ノード内部で扱われるそれぞれのノードの情報
    - name: 名前
    - endpoint: API エンドポイント
    - status: ノードの状態 (UP, DOWN)
    - down_count: ノードがダウンしたと確定するまでの猶予回数を記録
    """

    def __init__(self, name: str, endpoint: str, status: str | None = None, down_count: int = 0):
        self.name = name
        self.endpoint = endpoint
        self.status = status
        self.down_count = down_count

    def __lt__(self, other):
        return self.name < other.name

    def __str__(self):
        return f"ノード名: {self.name}, 状態: {self.status}, 無反応カウント: {self.down_count}"

async def check_node(target: Node) -> str | None:
    """
    入力されたノードに対して、稼働状況を確認する等の処理を行います。
    """

    if target.down_count is None:
        target.down_count = 0

    if target.name == utils.whoami():
        return None

    if config.LOG_LEVEL == "ALL":
        utils.print_log("[監視] ノード {} の動作状況を確認しています ...".format(target.name))

    res_dict = None

    try:
        while True:
            req_dict = {
                "url": target.endpoint,
            }
            
            r = await json_middleware.wrap(http_client.request)
            res_dict = await uasyncio.wait_for_ms(r(req_dict), 6000)

            try:
                _ = res_dict['status']['code']
            except KeyError:
                pass
            else:
                if config.LOG_LEVEL == "ALL":
                    utils.print_log("[監視] ノード " + target.name + " からレスポンスを受け取りました:")
                    print(res_dict)
                break

    except uasyncio.TimeoutError:
        if config.LOG_LEVEL == "ALL":
            utils.print_log("[監視] ノード " + target.name + " へのリクエストがタイムアウトしました。")

        await down_node(target)
        return str(target.name)

    if res_dict['status']['code'] != 200:
        if config.LOG_LEVEL == "ALL":
            utils.print_log("[監視] ノード " + target.name + " から不正なレスポンスを受け取りました。 (non-200 code)")
            
        await down_node(target)
        return str(target.name)

    if target.status == "NODE_DOWN":
        await recover_node(target)
        return str(target.name)

    if target.status is None or target.status == "NODE_UNKNOWN":
        target.status = "NODE_UP"

    if config.LOG_LEVEL == "ALL":
        utils.print_log("[監視] ノード {} は稼働しています。".format(target.name))

    target.down_count = 0
    return str(target.name)

async def down_node(target: Node):
    if target.status == "NODE_DOWN":
        if config.LOG_LEVEL == "ALL":
            utils.print_log("[監視] ノード {} はまだ障害を起こしています。".format(target.name))
        return

    if target.status != "NODE_DOWN":
        target.down_count = target.down_count + 1

    if target.down_count > 2 and target.status != "NODE_DOWN":
        utils.print_log("[監視] Node {} is now down.".format(target.name))
        target.status = "NODE_DOWN"

        await register_event(target, "NODE_DOWN")
    else:
        utils.print_log("[監視] ノード {} から反応が返ってきませんでした。 (確認ステージ: {} / 2)".format(target.name, target.down_count))

async def recover_node(target: Node):
    utils.print_log("[監視] ノード {} が復旧しました。".format(target.name))
    target.status = "NODE_UP"
    target.down_count = 0
    await register_event(target, "NODE_UP")

async def check_node_parallel():
    """
    check_node() を uasyncio を使って非同期的に実行します。
    """

    for node in config.NODES:
        await check_node(node)

    if config.LOG_LEVEL == "ALL":
        print("ノードの状況:")
        for node in config.NODES:
            if utils.whoami() != node.name:
                print(node)


async def register_event(node: Node, event_type: str):
    """
    イベントをノード内のイベント一覧に登録します。
    """

    # 新しくイベントの構造を定義する
    new_event = event.Event(
        origin=copy.copy(node.name),
        created_on=clock.get_epoch(),
        type=event_type,
        status="WAIT_CONFIRM",
        worker_node=[],
        majority_ok_on=None,
    )
    new_event.worker_node.append(utils.whoami())

    if config.LOG_LEVEL == "ALL":
        utils.print_log("イベントを登録しようとしています。内容は以下の通りです:\n" + str(new_event.__dict__))

    # 重複していれば、そこで処理を終わる
    identified = await event.identify_event(new_event)
    if identified is not None:
        return str(node.name)

    # 重複していなければ、登録する
    new_event_uuid = uuid.uuid4()
    event.events[str(new_event_uuid)] = new_event
    utils.print_log("[Event] イベントを登録しました: " + str(new_event_uuid))

    # 他のノードにこのイベントを共有する
    await event.share_event_parallel(
        "/event",
        event.events[str(new_event_uuid)],
        str(new_event_uuid)
    )
    utils.print_log("[Event] イベント " + str(new_event_uuid) + " をすべてのノードに共有しました。")
