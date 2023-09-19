import mip
import utime

import event


def auto_decode(query: bytes, encoding=["utf8", "cp1252"]):
    for i in encoding:
        try:
            return query.decode(i)
        except UnicodeDecodeError:
            pass


def enum(**enums: int):
    return type("Enum", (), enums)


def install_dependencies() -> None:
    mip.install("copy")


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
    return "{}/{}/{} {}:{}:{}".format(
        datetime_tuple[0],
        datetime_tuple[1],
        datetime_tuple[2],
        datetime_tuple[4],
        datetime_tuple[5],
        datetime_tuple[6],
    )


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
