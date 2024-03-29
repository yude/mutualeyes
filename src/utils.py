import utime
import network
import hashlib
import binascii

import config
import utils
import clock

def auto_decode(query: bytes, encoding=["utf8", "cp1252"]):
    for i in encoding:
        try:
            return query.decode(i)
        except Exception:
            return None


def enum(**enums: int):
    return type("Enum", (), enums)


def event_type_to_color(event_type: str) -> str:
    """
    イベントの種類に合う色を 10 進数で返します。
    """
    if event_type == "NODE_DOWN":
        return "16744319"

    if event_type == "NODE_UP":
        return "10616596"

    return "7697781"  # default


def format_epoch(epoch: int) -> str:
    """
    utime の日時タプルをフォーマットされた文字列で返します。
    """
    datetime_tuple = utime.localtime(epoch)
    return "{}/{}/{} {}:{:02}:{:02} UTC".format(
        datetime_tuple[0],
        datetime_tuple[1],
        datetime_tuple[2],
        datetime_tuple[3],
        datetime_tuple[4],
        datetime_tuple[5],
    )

def print_log(msg: str):
    epoch_source = clock.get_epoch()
    if clock.EPOCH_1970:
        epoch_source += 946684800

    print(f"{utils.format_epoch(epoch_source)}: {msg}")

def format_event_type(event_type: str) -> str:
    """
    イベントの種類を示す文字列のうち、内部で扱っているものから
    チャットツール等に表示するものに変換します。
    """
    if event_type == "NODE_UP":
        return "Up"

    if event_type == "NODE_DOWN":
        return "Down"

    return "Unknown"

def stringify_mac(mac_string):
    res = ""
    for b in mac_string:
        res += "%02x:" % (b)
    
    res = res[:-1]
    return res

def whoami() -> str:
    """
    自ノードが、登録されているノードのうちどれであるかを自動的に特定しようとします。
    """

    # config.ME が指定されていればそれを優先する
    if config.ME != "":
        return config.ME
    
    wlan = network.WLAN(network.STA_IF)

    # DHCP などで取得した IP アドレスから自動的に判別を試行する
    for node in config.NODES:
        sub_1 = "//"
        sub_2 = ":"

        idx_1 = node.endpoint.index(sub_1) - 1
        idx_2 = node.endpoint.rfind(sub_2)

        host = ''

        for idx in range(idx_1 + len(sub_1) + 1, idx_2):
            host = host + node.endpoint[idx]
        
        if host == wlan.ifconfig()[0]:
            config.ME = node.name
            return node.name
    
    # 特定失敗
    raise RuntimeError("Cannot detect whoami")

def get_healthy_node():
    """
    自ノードから見て正常に動作していると認識しているノードを返します。
    降順にソートしたものを返します。
    """
    healthy: list[str] = []
    for node in config.NODES:
        if node.status == "NODE_UP":
            healthy.append(node.name)
    
    healthy.sort()
    
    return healthy

class AuthHash:
    """
    ノード認証用のハッシュ値
    """
    def __init__(self, hash: str, created_on: int = clock.get_epoch()):
        self.hash = hash
        self.created_on = created_on

hashes: list[AuthHash] = []

async def get_auth_hash(seed: str)->str:
    """
    与えられたシード値と設定されているトークンからハッシュ値を生成します。
    """
    res = hashlib.sha256()
    token_plus_hash = bytes(config.TOKEN + seed, 'utf-8')
    res.update(token_plus_hash)

    return binascii.hexlify(res.digest()).decode('utf-8')

async def use_auth_hash(input_hash: str)->bool:
    """
    入力されたハッシュ値が認証用のものとして正しいか確認します。
    正しければ True, 間違っていれば False を返します。
    """
    for hash in hashes:
        if hash.hash == input_hash:
            return True
    
    return False

def number_nodes()->int:
    return len(config.NODES)
