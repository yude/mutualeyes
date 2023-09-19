import ntptime
import time

import constrants


def set_clock():
    """
    NTP を用いて RTC クロックの時刻を校正します。
    """
    # Retry 3 times
    for i in range(1, constrants.MAX_RETRY_NTP + 1):
        try:
            ntptime.settime()
        except Exception as e:
            print(
                "[Clock] Failed to retrieve current time from NTP, retrying. (Retry: {i}/{max_i})".format(
                    i=i, max_i=constrants.MAX_RETRY_NTP
                )
            )
            time.sleep(2)
        else:
            print("[Clock] Successfully retrieved current time.")
            return True

    print("[Clock] Failed to retrieve current time NTP, this system may won't work.")
    print("        Please re-check your Internet connection and configuration.")
    return False
