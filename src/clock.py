import machine
import ntptime

def set_clock():
    rtc = machine.RTC()
    ntptime.settime()