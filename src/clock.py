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
                "[Clock] Failed to retrieve current time from NTP, retrying. (Retry: {i}/{max_i})".format(
                    i=i, max_i=constrants.MAX_RETRY_NTP
                )
            )
            utime.sleep(2)
        else:
            print("[Clock] Successfully retrieved current time.")
            # エポックタイム 0 を 2000/1/1 00:00:00 UTC に統一する
            if utime.gmtime(0)[0] == 1970:
                EPOCH_1970 = True
            return True

    print("[Clock] Failed to retrieve current time NTP, this system may won't work.")
    print("        Please re-check your Internet connection and configuration.")
    return False

def get_epoch():
    global EPOCH_1970
    if EPOCH_1970:
        return utime.time() - 946684800
    else:
        return utime.time()
