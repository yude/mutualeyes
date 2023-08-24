import node

# ノードの設定
## 自分のノードの名前。
ME = "a"

# すべてのノードの定義
NODES: list[node.Node] = []
## ノード a
NODES.append(
    node.Node(
        name="a",
        endpoint="http://172.17.0.2:3000"
    )
)
## ノード b
NODES.append(
    node.Node(
        name="b",
        endpoint="http://172.17.0.3:3000"
    )
)
## ノード c
NODES.append(
    node.Node(
        name="c",
        endpoint="http://172.17.0.4:3000"
    )
)

# Wi-Fi
## 国別コード
WIFI_COUNTRY_CODE = "JP"
## アクセスポイントの SSID
WIFI_SSID = "eduroam"
## アクセスポイントの パスワード
WIFI_PASSWORD = ""

# http サーバー
HTTP_PORT = 3000
