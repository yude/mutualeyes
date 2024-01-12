# NTP サーバーから時刻を取得する際の最大再試行回数
MAX_RETRY_NTP = 5

# 他ノードのエンドポイントにアクセスする際のタイムアウト時間 (秒, float)
HTTP_GET_TIMEOUT = 2.5

# 以下のパラメーターはノード数に乗算されます。
## 同じイベントであるとみなすことのできる時間差の最大値 (秒, int)
SAME_EVENT_TIME_LAG = 5

## すべてのノードが特定のイベントを認知することを待機する時間 (秒, int)
EVENT_ACKNOWLEDGE_TIMEOUT = 8

## 他のノードに通知の配信を交代させるまでの待機時間 (秒, int)
EVENT_DELIVERY_TIMEOUT = 8

## イベント一覧のキャッシュから削除する時間 (分, int)
CLEAR_FROM_CACHE = 20
