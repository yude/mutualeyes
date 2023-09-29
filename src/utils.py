import utime
import network

import config
import utils

def auto_decode(query: bytes, encoding=["utf8", "cp1252"]):
    for i in encoding:
        try:
            return query.decode(i)
        except UnicodeDecodeError:
            pass


def enum(**enums: int):
    return type("Enum", (), enums)


def install_dependencies() -> None:
    # mip.install("copy")
    return


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
    print(utils.format_epoch(utime.time()) + ": " + msg)

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

def whoami():
    # Static detection
    if config.ME != "":
        return config.ME
    
    wlan = network.WLAN(network.STA_IF)

    # Automatically detect by local IP address
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