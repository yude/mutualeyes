from enum import Enum
import datetime

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
        type: EventType,
        status: EventStatus,
        worker_node: list
    ):
        self.source = source
        self.created_on = created_on
        self.type = type
        self.status = status
        self.worker_node = worker_node
