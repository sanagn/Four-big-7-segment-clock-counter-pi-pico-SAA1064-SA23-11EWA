from machine import I2C, Pin
import utime

# Δημιουργία του αντικειμένου I2C
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100000)
# η saa1604 ειναι παλιά συσκευή και τρεχει μεχρι 100000
# και γράφεται μόνο με  writeto_mem
# Διεύθυνση της συσκευής saa1064
device_address = 0x38

register = 0x00
reg = [0x01, 0x02, 0x03, 0x04]

t_list = bytearray([0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80])
t_list1 = bytearray([0x01, 0x03, 0x07, 0x0f, 0x1f, 0x3f, 0x7f, 0xff])

# Εγγραφή  (π.χ. εγγραφή της τιμής 0xFF στο register 0x10)
data_to_write = bytearray([0x77])
i2c.writeto_mem(device_address, register, data_to_write)
utime.sleep(0.1)
data_to_write = bytearray([0x01])
i2c.writeto_mem(device_address, 0x01, data_to_write)
utime.sleep(0.1)
data_to_write = bytearray([0x02])
i2c.writeto_mem(device_address, 0x02, data_to_write)
utime.sleep(0.1)
data_to_write = bytearray([0x04])

i2c.writeto_mem(device_address, 0x03, data_to_write)
print(hex(device_address), "0x03", data_to_write)
utime.sleep(0.1)
data_to_write = bytearray([0x08])
i2c.writeto_mem(device_address, 0x04, data_to_write)
utime.sleep(1)


while True:
 for i in t_list1:
  data_to_write = bytearray([i])
  for y in range(4):
   #data_to_write = bytearray([t_list])
   i2c.writeto_mem(device_address, reg[y], data_to_write)
   print(hex(device_address),", reg=", hex(reg[y]), " ", t_list)
   utime.sleep(0.03)
 utime.sleep(0.1)
 
 data_to_write = bytearray([0xf7])
 i2c.writeto_mem(device_address, register, data_to_write)
  