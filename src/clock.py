import ntptime
import utime

import constrants

EPOCH_1970 = False

def set_clock():
    global EPOCH_1970
    """
    NTP を用いて RTC クロックの時刻を校正します。
    """
    # Retry constrants.MAX_RETRY_NTP times
    for i in range(1, constrants.MAX_RETRY_NTP + 1):
        try:
            ntptime.settime()
        except Exception as e:
            print(
                "[RTC] NTP サーバーから現在日時を取得できませんでした。再試行します。 ({i}/{max_i})".format(
                    i=i, max_i=constrants.MAX_RETRY_NTP
                )
            )
            utime.sleep(2)
        else:
            print("[RTC] 現在日時を取得しました。")
            # エポックタイム 0 を 2000/1/1 00:00:00 UTC に統一する
            if utime.gmtime(0)[0] == 1970:
                EPOCH_1970 = True
            return True

    print("[RTC] NTP サーバーから現在時刻を取得できませんでした。システムが正常に稼働しない可能性があります。")
    print("        インターネット接続や設定を見直してください。")
    return False

def get_epoch():
    global EPOCH_1970
    if EPOCH_1970:
        return utime.time() - 946684800
    else:
        return utime.time()
