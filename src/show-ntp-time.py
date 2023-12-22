import wifi
import clock
import utime

wifi.prepare_wifi()
clock.set_clock()

while True:
    print(clock.get_epoch())
