import event
import constrants

# import datetime

def get_notify_workers(e: event.Event) -> str | None:
    """
    入力されたイベントの通知を配信すべきノードを返します。
    これは、通知すべき時刻からの経過時間によって変化することがあります。

    返り値が None のとき、入力されたイベントは、まだ「通知を配信する」ということが
    決定されていないはずです。
    """
    if e.confirmed_on is None:
        return None

    # 入力されたイベントの通知を配信すると確定してからの経過時間 (秒)
    diff = abs(
        datetime.datetime.now() - e.confirmed_on
    ).seconds

    # このイベントを認知しているノードのなかで、誰が配信するかを決定する
    # node_index は登録されているノードの名前を ascii 順に並べたときのインデックス
    node_index = diff / constrants.EVENT_DELIVERY_TIMEOUT
    if node_index > len(e.worker_node) - 1:
        node_index = len(e.worker_node) - 1
    
    return e.worker_node[node_index]
    

def send_to_discord(e: event.Event) -> bool:
    """
    入力されたイベントの通知を、
    Discord のテキストチャンネルに配信します。

    返り値は配信の成否です。
    """
    return True

def delivery(e: event.Event) -> bool:
    """
    事前定義された配信先に、入力されたイベントの通知を配信します。

    返り値は配信の成否です。
    """

    succeeded = True

    if send_to_discord(e) is False:
        succeeded = False

    return succeeded
