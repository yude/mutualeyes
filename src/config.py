from node import Node

# 認証
# 認証機能を使うかどうか。
USE_AUTH = False
# ランダムな文字列。SHA256 によるノードの偽造防止に使用されます。
TOKEN = "fipwerhferh"

# ノードの設定
## 自分のノードの名前。
ME = ""

# すべてのノードの定義
NODES: list[Node] = []

NODES += [Node("taurus", "http://192.168.1.101:3000")]
NODES += [Node("pegasus", "http://192.168.1.102:3000")]
NODES += [Node("orion", "http://192.168.1.103:3000")]
NODES += [Node("draco", "http://192.168.1.104:3000")]
NODES += [Node("lynx", "http://192.168.1.105:3000")]
NODES += [Node("vela", "http://192.168.1.106:3000")]


# ログ レベル
# ALL または DEFAULT
LOG_LEVEL = "ALL"

# Wi-Fi
## 国別コード
WIFI_COUNTRY_CODE = "JP"
## アクセスポイントの SSID
WIFI_SSID = "raspico"
## アクセスポイントの パスワード
WIFI_PASSWORD = "5F1BE41748"

## DHCP を使うかどうか。
WIFI_USE_DHCP = True
## 静的 IP アドレス
WIFI_STATIC_IP = '192.168.111.100'
## サブネットマスク
WIFI_SUBNET_MASK = '255.255.255.0'
## デフォルト ゲートウェイ
WIFI_DEFAULT_GATEWAY = '192.168.111.1'
## DNS サーバー
WIFI_DNS = '1.1.1.1'

# http サーバー
HTTP_PORT = 3000

# 通知先
## ntfy.sh
NTFYSH_URL = "http://ntfy.sh/2ab7eab87e27cc0d4559ea37339350da"
