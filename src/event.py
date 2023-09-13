import utime
import json
import copy
import uasyncio

import constrants
import config
import notify


class Event:
    def __init__(
        self,
        origin: str,  # イベントの発生元
        created_on: int,  # イベントの発生日時 (エポック以降の秒数)
        type: str,  # イベントの種類
        status: str,  # イベントの状態
        worker_node: list,  # イベントを認識しているノード
        confirmed_on: int | None,  # イベントの通知を配信すべき時刻 (エポック以降の秒数)
        source: str | None = None,  # イベントの取得元、POST リクエストの処理時に使用する
    ):
        self.origin = origin
        self.created_on = created_on
        self.type = type
        self.status = status
        self.worker_node = worker_node
        self.source = source
        self.confirmed_on = confirmed_on


events: dict[str, Event] = {}


def event_to_query(event: Event) -> str:
    """
    コード内で使用されているイベントのオブジェクトを、
    POST リクエスト等で使用できる JSON に変換します。
    """

    # このノードを、入力されたイベントが通過したということを記録します。
    e = copy.copy(event)
    e.source = config.ME
    e.worker_node.append(config.ME)
    worker_node_dict = set(copy.copy(e.worker_node))
    e.worker_node = list(worker_node_dict)

    return json.dumps(e.__dict__)  # type: ignore


def query_to_event(json_str: str) -> Event | None:
    """
    POST リクエスト等で受け取った JSON をパースして、
    コード内で使用されているイベント オブジェクトに変換します。
    """
    parsed_query = ""

    try:
        parsed_query = json.loads(json_str)
    except:  # noqa: E722
        return None

    event = Event(
        origin=parsed_query.origin,
        created_on=int(parsed_query.created_on),
        type=parsed_query.event_type,
        status="WAIT_CONFIRM",
        worker_node=[config.ME],
        confirmed_on=None,
    )

    return event


async def identify_event(target: Event) -> Event | None:
    """
    入力のイベントに関して、既にこのノード内に同じものとしてみなせる
    イベントがある場合、それを返します。存在しない場合、None を返します。
    """

    for e in events:
        # イベントの発生元 (ターゲット) とイベントの種類が等しい
        if events[e].origin == target.origin and events[e].type == target.type:
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
    - 指定時間経過していたら合意処理を行う
    - EventStatus の更新を行う
    - ...
    """
    e = events[event_id]

    if e.status == "DELIVERED":  # 既に通知を配信済み
        return event_id

    if e.status == "WAIT_CONFIRM":  # 通知の配信の決定待ち
        diff = abs(e.created_on - utime.time())
        if diff < 60 * constrants.EVENT_ACKNOWLEDGE_TIMEOUT:  # イベント作成から一定時間内
            # 何もしない
            return event_id

        e.status = "WAIT_DELIVERY"

    if e.status == "WAIT_DELIVERY":  # 通知の配信待ち
        delivery_actor = notify.get_notify_workers(e)
        if delivery_actor == config.ME:
            succeeded = notify.delivery(event_id)
            if succeeded:
                e.status = "DELIVERED"

    return event_id


async def check_event_parallel():
    for e in uasyncio.as_completed([check_event(event_id) for event_id in events]):
        finished_event = await e

        print("Scheduled tasks for event {} is finished.".format(finished_event))

    uasyncio.sleep(5)
