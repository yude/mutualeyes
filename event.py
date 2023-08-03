from enum import Enum
import datetime
import json

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
        source: str,
        created_on: datetime.datetime,
        type: int,
        status: int,
        worker_node: list
    ):
        self.source = source
        self.created_on = created_on
        self.type = type
        self.status = status
        self.worker_node = worker_node


events: list[Event] = []

async def event_to_query(event: Event) -> str:
    """
    コード内で使用されているイベントのオブジェクトを、
    POST リクエスト等で使用できる JSON に変換します。
    """

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
        event.__dict__,
        default=serialize_default # type: ignore
    )


async def query_to_event(json_str: str) -> Event | None:  # noqa: E1131
    """
    POST リクエスト等で受け取った JSON をパースして、
    コード内で使用されているイベント オブジェクトに変換します。
    """
    parsed_query = ""
    created_on = datetime.time()

    try:
        parsed_query = json.loads(json_str)
    except:
        return None
    
    try:
        created_on = datetime.datetime.strptime(
            q.created_on,
            "%Y-%m-%d %H:%M:%S"
        )
    except:  # noqa: E722
        return None
    
    if q.type == "up":
        event_type = EventType.UP
    elif q.type == "down":
        event_type = EventType.DOWN
    else:
        event_type = EventType.UNKNOWN

    event = Event(
        source=parsed_query.source,
        created_on=created_on,
        type=event_type,
        status=EventStatus.WAIT_CONFIRM,
        worker_node=[]
    )

    return event


async def identify_event(event: Event) -> Event | None:  # noqa: E1131
    """
    入力のイベントに関して、既にこのノード内に同じものとしてみなせる
    イベントがある場合、それを返します。存在しない場合、None を返します。
    """


    return None
