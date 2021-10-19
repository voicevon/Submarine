from adafruit_servokit import ServoKit
from adafruit_pca9685 import PCA9685
import board
import busio
import time
text_address = 0x40
i2c_bus0=(busio.I2C(board.SCL_1,board.SDA_1,frequency=400000))
my=ServoKit(channels=16,i2c=i2c_bus0,address=text_address,frequency=49.5)

t=0.0
test_id = 2


middle = 83.50
offset = 0.00
step = 1
pwm_channel = 8
pwm_channel_servo = 1

while test_id == 1 :
    for i in range(14,16):
       print("servoo_id=",i)
       for ang in range(12,30):
           my.servo[i].angle=ang
           print("angle=",ang)
           if ang==90:
              print("sleep")
              time.sleep(5)
           my.servo[i].angle=0 
           time.sleep(1)  
       time.sleep(5)
    print("working")
    time.sleep(3)

    for i in range(14,16):
       my.servo[i].angle=0    
    print("return")
    time.sleep(3)

while  test_id ==2:

   ang = 90
  
   my.servo[15].angle=ang
   print("servoo_id=15" , "angle=",ang)
   time.sleep(3)
   # print("server_id=",servo_id)      
   #time.sleep(5)
   print("working")
   time.sleep(3)

   for i in range(0,16):
      my.servo[i].angle=0    
   print("return")
   time.sleep(3)
while test_id ==3:



   delay = 1

   position = middle + offset
   my.servo[pwm_channel].angle = position
   my.servo[pwm_channel_servo].angle = position
   print("postion" , position,"+++++")
   time.sleep(delay)
   offset = offset + step
   print("         ", offset,"offset = ")

   position = middle - offset
   my.servo[pwm_channel].angle = position
   my.servo[pwm_channel_servo].angle = position
   print(position,"----")
   time.sleep(delay)

while test_id ==4:



   delay = 1

   position = middle + offset
   my.servo[pwm_channel].angle = position
   my.servo[pwm_channel_servo].angle = position
   print("postion" , position,"+++++")
   time.sleep(delay)
   offset = offset + step
   print("         ", offset,"offset = ")
   time.sleep(delay)
while test_id ==5:
   delay = 1
   position = middle - offset
   my.servo[pwm_channel].angle = position
   offset = offset + step
   print("         ", offset,"offset = ")

   position = middle - offset
   my.servo[pwm_channel_servo].angle = position
   print(position,"----")
   time.sleep(delay)

   
