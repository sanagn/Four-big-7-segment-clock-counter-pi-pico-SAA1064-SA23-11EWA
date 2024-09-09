#must remove all print
from machine import Pin, I2C
from saa1064 import SAA1064
import utime

# time
import socket
import time
import struct
NTP_DELTA = 2208988800
host = "pool.ntp.org"
'''
Η Greenwich Mean Time ειναι 2 ώρες πίσω από την ώρα στην Αθήνα όταν η Αθήνα
είανι σε κανονική ώρα, και 3 ώρες πίσω από την Αθήνα όταν η Αθήνα είναι σε καλοκαιρινή (daylight saving time).
'''
led = Pin("LED", Pin.OUT)
# oper socket fich time for ntp
def set_time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    print("uu")
    t = val - NTP_DELTA    
    tm = time.gmtime(t)
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
    
set_time()
print(time.localtime())

# Initialize I2C on the appropriate pins for your board (e.g., ESP32)
# Adjust SCL and SDA pins based on your board
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100000)  # alway freq=100000
saa1064 = SAA1064(i2c)

saa1064.init_display()
# Set brightness level (0-7)
saa1064.set_brightness(5)

while True:
 #timestamp=rtc.datetime()
 timestamp = time.localtime()   
 hour = int(timestamp[3])  # Παίρνουμε το στοιχείο στη θέση 4
 minute = int(timestamp[4])  # Παίρνουμε το στοιχείο στη θέση 5
 second = int(timestamp[5])
 timestring = "%02d%02d" % (hour, minute)
 print("time is: ",str(timestring))
 if second % 2 == 1:
   text = str(timestring)
   # Display digits 1, 2, 3, 4
   saa1064.display_digit_dp(text)
 else:
   text = str(timestring)
   # Display digits 1, 2, 3, 4
   saa1064.display_digit(text)
 utime.sleep(1)

