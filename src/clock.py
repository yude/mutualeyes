import machine
import ntptime

def set_clock():
    rtc = machine.RTC()
    try:
        ntptime.settime()
    except OSError:
        print("[Warning] Failed to retrieve current time from NTP.")