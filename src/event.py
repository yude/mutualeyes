import utime
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

class EventQuery:
    def __init__(
        self,
        event: dict,
        sent_from: str,
    ):
        self.event = event
        self.sent_from = sent_from


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

    if config.LOG_LEVEL == "ALL":
        utils.print_log(f"[Query2Event] Loaded following JSON: {json_str}")

    event = Event(
        origin=q["event"]["origin"],
        created_on=int(q["event"]["created_on"]),
        type=q["event"]["type"],
        status="WAIT_CONFIRM",
        worker_node=[],
        majority_ok_on=None
    )

    event.worker_node.append(q["sent_from"])
    event.worker_node.append(utils.whoami())
    event.worker_node = list(set(event.worker_node))

    if config.LOG_LEVEL == "ALL":
        utils.print_log("[Query2Event] Query has been converted to event: ")
        print(event.__dict__)

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
                < constrants.SAME_EVENT_TIME_LAG * 60
            ):
                return events[e]

    return None


async def check_event(event_id: str) -> str:
    """
    入力されたイベントに対して、次のような処理を行います。
    - 過半数のノードが合意しているかを確認する。
    - 過半数のノードが合意していたら通知を行う。
    - イベントの状態の更新を行う。
    - ...
    """

    e = events[event_id]

    # タイムアウト、または古いイベントは削除
    if abs(e.created_on - utime.time()) > 60 * constrants.CLEAR_FROM_CACHE:
        events.pop(event_id)

        if config.LOG_LEVEL == "ALL":
            utils.print_log("[Event] Event " + event_id + " is deleted from cache.")

        return event_id

    # 既に通知を配信済み
    if e.status == "DELIVERED":
        return event_id

    # 通知の配信の決定待ち
    if e.status == "WAIT_CONFIRM":
        if abs(e.created_on - utime.time()) > constrants.EVENT_ACKNOWLEDGE_TIMEOUT:
            # 過半数が合意したかを確認
            try:
                ratio = len(e.worker_node) / len(utils.get_healthy_node())
            except ZeroDivisionError:
                # 自分しか稼働しているノードが存在しないとき、強制的に通知待機状態にする
                ratio = 1.0
            if ratio >= 0.5:
                e.majority_ok_on = utime.time()
                utils.print_log("[Event] Majority of nodes agreed w/ event " + event_id + ".")
                e.status = "WAIT_DELIVERY"
            else:
                # タイムアウトしたイベントは削除
                events.pop(event_id)
                utils.print_log("[Event] Event " + event_id + " is timed out.")
            return event_id

    # 通知の配信待ち
    if e.status == "WAIT_DELIVERY":
        delivery_actor = await notify.get_notify_workers(e)
        if delivery_actor == utils.whoami():
            succeeded = await notify.delivery(event_id)
            if succeeded:
                e.status = "DELIVERED"
                utils.print_log("[Event] Event " + event_id + " is delivered.")

    return event_id


async def check_event_parallel():
    if config.LOG_LEVEL == "ALL":
        print("Current events: " + str(events.keys()))
    tasks = [check_event(event_id) for event_id in events.keys()]
    await uasyncio.gather(*tasks)

async def share_event(path: str, event: Event, event_id: str, n: node.Node):
    if n.name == utils.whoami():
        return

    res_dict = None
    q = EventQuery(
        event=event.__dict__,
        sent_from=utils.whoami()
    ).__dict__

    if config.LOG_LEVEL == "ALL":
        utils.print_log("Sharing event " + event_id + " to other nodes. Request body is following:")
        print(json.dumps(q))

    try:
        while True:
            req_dict = {
                "url": n.endpoint + path,
                "headers": {
                    "Accept": "application/json"
                },
                "method": "POST",
                "body": q
            }

            r = await json_middleware.wrap(http_client.request)
            res_dict = await uasyncio.wait_for_ms(r(req_dict), 1500)

            try:
                _ = res_dict['status']['code']
            except KeyError:
                pass
            else:
                break

    except Exception:
        if config.LOG_LEVEL == "ALL":
            utils.print_log("[Event] Failed to share event " + event_id + " to node " + n.name + ".")
        return

    if res_dict['status']['code'] != 200:
        if config.LOG_LEVEL == "ALL":
            utils.print_log("[Event] Failed to share event " + event_id + " to node " + n.name + ".")
        return

async def share_event_parallel(path: str, event: Event, event_id: str):
    tasks = [share_event(path, event, event_id, n) for n in config.NODES]
    await uasyncio.gather(*tasks)
