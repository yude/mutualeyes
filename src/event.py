import clock
import json
import copy
import uasyncio

import utils
import constrants
import config
import notify
import node
import http_client.core as http_client
import http_client.json_middleware as json_middleware

class Event:
    """
    ノード内部で扱われるイベントの実体
    """
    def __init__(
        self,
        origin: str,  # イベントの発生元
        created_on: int,  # イベントの発生日時 (エポック以降の秒数)
        type: str,  # イベントの種類
        status: str,  # イベントの状態
        worker_node: list[str],  # イベントを認識しているノード
        majority_ok_on: int | None,  # 過半数が合意した時刻
    ):
        self.origin = origin
        self.created_on = created_on
        self.type = type
        self.status = status
        self.worker_node = worker_node
        self.majority_ok_on = majority_ok_on

    def __lt__(self, other):
        return self.created_on < other.created_on

    def __str__(self):
        return f'発生元: {self.origin}, 作成日時: {self.created_on}, 種類: {self.type}, 状態: {self.status}, ワーカー: {self.worker_node}, 合意日時: {self.majority_ok_on}'

class EventQuery:
    """
    他のノードへ送信するイベントの実体
    """
    def __init__(
        self,
        event: dict,
        sent_from: str,
        hash: str,
    ):
        self.event = event
        self.sent_from = sent_from
        self.hash = hash


events: dict[str, Event] = {}


def query_to_event(json_str: str) -> Event | None:
    """
    POST リクエストで受け取った JSON をパースして、
    コード内で使用されているイベント オブジェクトに変換します。
    """
    q = ""

    try:
        q = json.loads(json_str)
    except:  # noqa: E722
        return None

    event = Event(
        origin=q["event"]["origin"],
        created_on=int(q["event"]["created_on"]),
        type=q["event"]["type"],
        status=q["event"]["status"],
        worker_node=[],
        majority_ok_on=None
    )

    event.worker_node.append(q["sent_from"])
    event.worker_node.append(utils.whoami())
    event.worker_node = list(set(event.worker_node))

    return event


async def identify_event(target: Event) -> Event | None:
    """
    入力のイベントに関して、既にこのノード内に同じものとしてみなせる
    イベントがある場合、それを返します。存在しない場合、None を返します。
    """

    for e in events:
        # イベントの発生元 (ターゲット) が等しい
        if events[e].origin == target.origin:
            # イベントの発生日時の差が一定の値に収まっているかを確認する
            if (
                abs(events[e].created_on - target.created_on)
                < utils.number_nodes() * constrants.SAME_EVENT_TIME_LAG * 60
            ):
                if events[e].type == target.type:
                    if config.LOG_LEVEL == "ALL":
                        utils.print_log("既知のイベントとして判別しました: \n" + str(target.__dict__))
                    return events[e]

    if config.LOG_LEVEL == "ALL":
        utils.print_log("未知のイベントとして判別しました: \n" + str(target.__dict__))

    return None


async def check_event(event_id: str) -> str:
    """
    入力されたイベントに対して、次のような処理を行います。
    - 過半数のノードが合意しているかを確認する。
    - 過半数のノードが合意していたら発報を行う。
    - イベントの状態の更新を行う。
    """

    e = events[event_id]

    # タイムアウト、または古いイベントは削除
    if abs(e.created_on - clock.get_epoch()) > 60 * constrants.CLEAR_FROM_CACHE * utils.number_nodes():
        events.pop(event_id)

        if config.LOG_LEVEL == "ALL":
            utils.print_log("[Event] イベント " + event_id + " はキャッシュから削除されました。")

        return event_id

    # 既に通知を配信済み
    if e.status == "DELIVERED":
        return event_id

    # 通知の配信の決定待ち
    if e.status == "WAIT_CONFIRM":
        if abs(e.created_on - clock.get_epoch()) > constrants.EVENT_ACKNOWLEDGE_TIMEOUT * utils.number_nodes():
            # 過半数が合意したかを確認
            try:
                ratio = len(e.worker_node) / len(utils.get_healthy_node())
            except ZeroDivisionError:
                # 自分しか稼働しているノードが存在しないとき、強制的に通知待機状態にする
                ratio = 1.0
            if ratio >= 0.5:
                e.majority_ok_on = clock.get_epoch()
                utils.print_log("[Event] 過半数のノードがイベント " + event_id + " の発生を合意しました。")
                e.status = "WAIT_DELIVERY"
            else:
                # タイムアウトしたイベントは削除
                events.pop(event_id)
                utils.print_log("[Event] イベント " + event_id + " は合意されませんでした。削除されます。")
            return event_id

    # 通知の配信待ち
    if e.status == "WAIT_DELIVERY":
        delivery_actor = await notify.get_notify_worker(e)
        if delivery_actor == utils.whoami():

            if delivery_actor == e.origin:
                return event_id
            
            succeeded = await notify.delivery(event_id)
            if succeeded:
                e.status = "DELIVERED"
                utils.print_log("[Event] イベント " + event_id + " は発報されました。")

    return event_id


async def check_event_parallel():
    """
    並列的にイベントを処理します。
    """
    if config.LOG_LEVEL == "ALL":
        print("有効なイベント:")
        for k, v in events.items():
            print(f"[{k}] {v}")
    tasks = [check_event(event_id) for event_id in events.keys()]
    await uasyncio.gather(*tasks)

async def share_event(path: str, event: Event, event_id: str, query: EventQuery, n: node.Node):
    """
    与えられたイベントの情報を、他のノードで共有します。
    """

    if n.name == utils.whoami():
        return

    res_dict = None

    if config.USE_AUTH:
        # 認証のためのシード部分を相手ノードから取得する
        try:
            req_dict = {
                    "url": n.endpoint + "/get-seed",
                }

            res_dict = await uasyncio.wait_for_ms(http_client.request(req_dict), 5000)

        except Exception:
            if config.LOG_LEVEL == "ALL":
                utils.print_log("[Event] ノード " + n.name + " と安全な接続を確立できませんでした。")
            return

        if res_dict['status']['code'] != 200:
            if config.LOG_LEVEL == "ALL":
                utils.print_log("[Event] ノード " + n.name + " と安全な接続を確立できませんでした。")
            return
        
        # 取得したシード値は bytes 型で b'シード'\r\n のようになっているため、シード値のみ取り出す
        # 取り出したものを utils.get_auth_hash() に入力してハッシュ化する
        query.hash = await utils.get_auth_hash(
            res_dict['body'].decode('utf-8').replace('\n', '').replace('\r', '')
        )

    # 相手のノードにイベントの情報を送信する
    try:
        while True:
            req_dict = {
                "url": n.endpoint + path,
                "headers": {
                    "Accept": "application/json"
                },
                "method": "POST",
                "body": query.__dict__
            }

            r = await json_middleware.wrap(http_client.request)
            res_dict = await uasyncio.wait_for_ms(r(req_dict), 5000)

            try:
                _ = res_dict['status']['code']
            except KeyError:
                pass
            else:
                break

    except Exception:
        if config.LOG_LEVEL == "ALL":
            utils.print_log("[Event] イベント " + event_id + " をノード " + n.name + " と共有できませんでした。")
        return

    if res_dict['status']['code'] != 200:
        if config.LOG_LEVEL == "ALL":
            utils.print_log("[Event] イベント " + event_id + " をノード " + n.name + " と共有できませんでした。")
            print(res_dict)
        return

async def share_event_parallel(path: str, event: Event, event_id: str):
    """
    他のノードにイベントを共有します。
    これは並列処理のために用意されています。
    """

    q = EventQuery(
        event=event.__dict__,
        sent_from=utils.whoami(),
        hash="",
    )

    if config.LOG_LEVEL == "ALL":
        utils.print_log("イベント " + event_id + " を他のノードと共有します。リクエスト ボディは以下の通りです:")
        print(json.dumps(q.__dict__))

    for n in config.NODES:
        await share_event(path, event, event_id, q, n)
