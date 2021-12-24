from sensor.water_depth_sensor import WaterDepthSensor
# from  adafruit_servokit import ServoKit
from adafruit_pca9685 import PCA9685

# import board
import busio
import time

class CAMERA_POSITION:
    FRONT = 1
    BACK = 2
    LEFT = 3
    RIGHT = 4
    TOP = 5
    BOTTOM = 6

class MOVE_DIRECTION:
    FORWARD = 1
    BACKWARD = 2
    LEFT = 3
    RIGHT = 4
    UP = 5
    DOWN = 6
    TURN_LEFT = 7
    TURN_RIGHT = 8


class MOTOR_CHANNEL:
    TOP_XPYP = 11
    TOP_XNYP = 15
    TOP_XNYN = 14
    TOP_XPYN = 10
    BOTTOM_XPYP = 9
    BOTTOM_XNYP = 13
    BOTTOM_XNYN = 12
    BOTTOM_XPYN = 8

class Propellers():
    '''
    Manage PWM output
    Upper layer will never know what is PWM, channel.

    '''

    def __init__(self, i2c_bus: busio.I2C):
        # init PCA9685
        pwm_controller_address = 0x40
        # self.motors = ServoKit(channels=16, i2c=i2c_bus, address=pwm_controller_address, frequency=49.5)
        self.motors = PCA9685(i2c_bus)
        self.motors.frequency = 49.5
        self.motors.channels[MOTOR_CHANNEL.TOP_XNYN].duty_cycle = 0x7FFF
        time.sleep(1)
        self.motors.channels[MOTOR_CHANNEL.TOP_XNYN].duty_cycle = 0x3FFF
        # self.current_speed = [0,0,0,0, 0,0,0,0]
        print("cccccccccccccccccccccccccccccccccccccccccccccccccccccccc")

    def StartSingleMotor(self, channel_id:int):
        print("   -------------------", channel_id)
        self.motors.servo[channel_id].angle = 90
        print("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
        # self.TestSingleMotor(channel_id)
    

    def TestSingleMotor(self,channel_id:int):
        print("   Runing CW  10 seconds  ", channel_id)
        self.motors.servo[channel_id].angle = 70
        time.sleep(10)
        print("       Sleeping  10 seconds   ")
        self.motors.servo[channel_id].angle = 90
        time.sleep(10)


    def StartAllMotors(self):
        self.StartSingleMotor(MOTOR_CHANNEL.TOP_XPYP)
        self.StartSingleMotor(MOTOR_CHANNEL.TOP_XNYP)
        self.StartSingleMotor(MOTOR_CHANNEL.TOP_XNYN)
        self.StartSingleMotor(MOTOR_CHANNEL.TOP_XPYN)
        self.StartSingleMotor(MOTOR_CHANNEL.BOTTOM_XPYP)
        self.StartSingleMotor(MOTOR_CHANNEL.BOTTOM_XNYP)
        self.StartSingleMotor(MOTOR_CHANNEL.BOTTOM_XNYN)
        self.StartSingleMotor(MOTOR_CHANNEL.BOTTOM_XPYN)
        time.sleep(1)
        print('     Motor as servo is Started.... ')

    def StopAllMotors(self):
        self.StartAllMotors()


    def __move_up_down(self, speed):
        '''
        Turn on PWM # 1,2,3,4  at the speed
        '''
        self.my.servo[8].angle = 90
        self.my.servo[9].angle = 90
        self.my.servo[10].angle = 90
        self.my.servo[11].angle = 90
        

    def move_forward(self, speed):
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XNYN].angle = 90 - speed
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XPYN].angle = 90 - speed
        
    
    def move_backward(self, speed):
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XNYP].angle = 90 + speed
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XPYP].angle = 90 + speed

    # def move_left(self, speed_clockwise,speed_counterclockwise):
    def move_left(self, speed):
        '''
        Can be 2 motors or 4 motors, We choose 2 motors.
        '''
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XPYN].angle = 90 + speed
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XPYP].angle = 90 - speed

    def move_right(self, speed):
        '''
        Can be 2 motors or 4 motors
        '''
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XNYN].angle = 90 + speed
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XNYP].angle = 90 - speed

    def move_up(self, speed, to_water_depth):
        self.motors.servo[MOTOR_CHANNEL.TOP_XPYP].angle = 90 + speed
        self.motors.servo[MOTOR_CHANNEL.TOP_XNYP].angle = 90 + speed
        self.motors.servo[MOTOR_CHANNEL.TOP_XNYN].angle = 90 + speed
        self.motors.servo[MOTOR_CHANNEL.TOP_XPYN].angle = 90 + speed


    def move_down(self, speed ,to_water_depth):
        self.motors.servo[MOTOR_CHANNEL.TOP_XPYP].angle = 90 - speed
        self.motors.servo[MOTOR_CHANNEL.TOP_XNYP].angle = 90 - speed
        self.motors.servo[MOTOR_CHANNEL.TOP_XNYN].angle = 90 - speed
        self.motors.servo[MOTOR_CHANNEL.TOP_XPYN].angle = 90 - speed
    
    def turn_left(self, speed:int):
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XPYP].angle = 90 - speed
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XNYN].angle = 90 + speed

    def turn_right(self,speed:int) -> None:
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XPYP].angle = 90 + speed
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XNYN].angle = 90 - speed
    
    def spin(self):
        '''
        This will run at a new thread. to keep the water_depth_position
        '''
        current_depth = self.__water_depth_sensor.read_water_depth()
        if current_depth < self.__target_water_depth -1 :

            # should move down

            target = self.__target_water_depth
            Propeller.move_down(10,target)
        elif current_depth > self.__target_water_depth + 1:

            # should move up
            
            target = self.__target_water_depth
            Propeller.move_up(10,target)
            
        else: 
            speed = 90
        self.__move_up_down(speed)
