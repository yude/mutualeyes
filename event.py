from enum import Enum
from typing import Union
import datetime
import json
import copy
import config

class EventType(Enum):
    UP = 1
    DOWN = 2
    UNKNOWN = 3

class EventStatus(Enum):
    # このイベントに対して、通知を発行するまでの待機状態
    WAIT_CONFIRM = 1
    # このイベントに対して、通知を発行したことを確認した状態
    EVENT_DONE = 2

class Event:
    def __init__(
        self,
        origin: str,  # イベントの発生元
        created_on: datetime.datetime,  # イベントの発生日時
        type: int,  # イベントの種類, event.EventType を使用する
        status: int,  # イベントの状態, event.EventStatus を使用する
        worker_node: list,  # イベントを認識しているノード
        source: Union[str, None] = None  # イベントの取得元、POST リクエストの処理時に使用する
    ):
        self.origin = origin
        self.created_on = created_on
        self.type = type
        self.status = status
        self.worker_node = worker_node
        self.source = source


events: dict[str, Event] = {}

async def event_to_query(event: Event) -> str:
    """
    コード内で使用されているイベントのオブジェクトを、
    POST リクエスト等で使用できる JSON に変換します。
    """

    # このノードを、入力されたイベントが通過したということを記録します。
    e = copy.copy(event)
    e.source = config.ME
    e.worker_node.push(config.ME)
    worker_node_dict = set(copy.copy(e.worker_node))
    e.worker_node = list(worker_node_dict)

    # 適当なフォーマットに整形します。
    def serialize_default(obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        
        if isinstance(obj, EventType):
            if obj is EventType.UP:
                return "up"
            if obj is EventType.DOWN:
                return "down"
            return "unknown"
        
        raise TypeError("Type %s is not serializable" % type(obj))

    return json.dumps(
        e.__dict__,
        default=serialize_default  # type: ignore
    )


async def query_to_event(json_str: str) -> Union[Event, None]:
    """
    POST リクエスト等で受け取った JSON をパースして、
    コード内で使用されているイベント オブジェクトに変換します。
    """
    parsed_query = ""
    created_on = datetime.time()

    try:
        parsed_query = json.loads(json_str)
    except:  # noqa: E722
        return None
    
    try:
        created_on = datetime.datetime.strptime(
            parsed_query.created_on,
            "%Y-%m-%d %H:%M:%S"
        )
    except:  # noqa: E722
        return None
    
    if parsed_query.type == "up":
        event_type = EventType.UP
    elif parsed_query.type == "down":
        event_type = EventType.DOWN
    else:
        event_type = EventType.UNKNOWN

    event = Event(
        origin=parsed_query.origin,
        created_on=created_on,
        type=event_type,
        status=EventStatus.WAIT_CONFIRM,
        worker_node=[config.ME]
    )

    return event


async def identify_event(target: Event) -> Union[Event, None]:
    """
    入力のイベントに関して、既にこのノード内に同じものとしてみなせる
    イベントがある場合、それを返します。存在しない場合、None を返します。
    """

    for e in events:
        # イベントの発生元 (ターゲット) とイベントの種類が等しい
        if (
            events[e].origin == target.origin and
            events[e].type == target.type
        ):
            # イベントの発生日時の差が 5 分以内
            if (
                abs(events[e].created_on - target.created_on) <
                datetime.timedelta(minutes=5)
            ):
                return events[e]

    return None
