import event
import constrants
import clock
import utils
import config
import http_client.core as http_client
import http_client.json_middleware as json_middleware

import utime
import math
import uasyncio
import urequests
import ujson
import gc


async def get_notify_worker(e: event.Event) -> str | None:
    """
    入力されたイベントの通知を配信すべきノードを返します。
    これは、通知すべき時刻からの経過時間によって変化することがあります。

    返り値が None のとき、入力されたイベントは、まだ「通知を配信する」ということが
    決定されていないはずです。
    """

    # 重複を削除
    e.worker_node = list(set(e.worker_node))
    # ASCII 順にソート
    e.worker_node = [i for _, i in sorted(zip([sum(map(ord, x)) for x in e.worker_node], e.worker_node), reverse=False)]

    if e.majority_ok_on is None:
        return None

    # 入力されたイベントの通知を配信すると確定してからの経過時間 (秒)
    diff = abs(clock.get_epoch() - e.majority_ok_on)

    # このイベントを認知しているノードのなかで、誰が配信するかを決定する
    # node_index は登録されているノードの名前を ascii 順に並べたときのインデックス
    node_index = math.floor(diff / constrants.EVENT_DELIVERY_TIMEOUT * utils.number_nodes())
    if node_index > len(e.worker_node) - 1:
        node_index = len(e.worker_node) - 1

    return e.worker_node[node_index]

async def send_to_ntfy(event_id: str) -> bool:
    """
    入力されたイベントの通知を、
    ntfy.sh に送信します。

    返り値は配信の成否です。
    """

    e = event.events[event_id]
    if e.status == "DELIVERED":
        return True

    try:
        while True:
            req_dict = {
                "url": config.NTFYSH_URL,
                "method": "POST",
                "header": {
                    "Content-Type": "text/markdown",
                },
                "body": f"{e.origin} is now {utils.format_event_type(e.type)} ({utils.format_epoch(e.created_on)}, Sent from {utils.whoami()})"
            }

            if config.LOG_LEVEL == "ALL":
                utils.print_log("イベント " + event_id + " を ntfy.sh に発報します。リクエスト ボディは以下の通りです:")
                print(req_dict)

            r = await json_middleware.wrap(http_client.request)
            res_dict = await uasyncio.wait_for_ms(r(req_dict), 1500)

            try:
                _ = res_dict['status']['code']
            except KeyError:
                pass
            else:
                break

    except Exception as e:
        utils.print_log(f"[警告] イベント {event_id} を ntfy.sh に送信できませんでした。 ({e})")
        return False

    if res_dict['status']['code'] != 200:
        msg = f"[警告] イベント {event_id} を ntfy.sh に送信できませんでした。 (non-200 code"
        try:
            msg += ", " + res_dict['body'] + ")"
        except KeyError:
            msg += ")"

        if config.LOG_LEVEL == "ALL":
            utils.print_log(msg)
        return False

    return True


async def delivery(event_id: str) -> bool:
    """
    事前定義された配信先に、入力されたイベントの通知を配信します。

    返り値は配信の成否です。
    """

    succeeded = True

    if await send_to_ntfy(event_id) is False:
        succeeded = False
    
    if succeeded:
        await event.share_event_parallel(
            "/notify-done",
            event.events[event_id],
            event_id
        )
    
    utils.print_log("[Event] イベント " + event_id + " を発報したことを他のノードと共有しました。")

    return succeeded
