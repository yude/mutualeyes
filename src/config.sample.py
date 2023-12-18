import node

# ノードの設定
## 自分のノードの名前。
ME = ""

# すべてのノードの定義
NODES: list[node.Node] = []

NODES += [node.Node("a", "http://a:3000")]
NODES += [node.Node("b", "http://b:3000")]
NODES += [node.Node("c", "http://c:3000")]

# ログ レベル
# ALL または DEFAULT
LOG_LEVEL = "ALL"

# Wi-Fi
## 国別コード
WIFI_COUNTRY_CODE = "JP"
## アクセスポイントの SSID
WIFI_SSID = ""
## アクセスポイントの パスワード
WIFI_PASSWORD = ""

## DHCP を使うかどうか。
WIFI_USE_DHCP = True
## 静的 IP アドレス
WIFI_STATIC_IP = ''
## サブネットマスク
WIFI_SUBNET_MASK = ''
## デフォルト ゲートウェイ
WIFI_DEFAULT_GATEWAY = ''
## DNS サーバー
WIFI_DNS = ''

# http サーバー
HTTP_PORT = 3000

# 通知先
## ntfy.sh
NTFYSH_URL = ""
