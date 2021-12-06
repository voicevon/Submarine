from sensor.water_depth_sensor import WaterDepthSensor
from  adafruit_servokit import ServoKit
# from adafruit_pca9685 import PCA9685

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
        self.motors = ServoKit(channels=16, i2c=i2c_bus, address=pwm_controller_address, frequency=49.5)
        # self.current_speed = [0,0,0,0, 0,0,0,0]

    def StartSingleMotor(self, channel_id:int):
        print("   -------------------", channel_id)
        self.motors.servo[channel_id].angle = 90
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
        # self.motors.servo[MOTOR_CHANNEL.TOP_XPYP].angle = 90
        # print('  111111111 ')
        # time.sleep(test_delay)
        # self.motors.servo[MOTOR_CHANNEL.TOP_XPYP].angle = 80
        # time.sleep(3)
        # self.motors.servo[MOTOR_CHANNEL.TOP_XPYP].angle = 90

        
        # self.motors.servo[MOTOR_CHANNEL.TOP_XNYP].angle = 90
        # print('  222222222222 ')
        # time.sleep(test_delay)
        # self.motors.servo[MOTOR_CHANNEL.TOP_XNYN].angle = 90
        # print('  33333333333 ')
        # time.sleep(test_delay)
        # self.motors.servo[MOTOR_CHANNEL.TOP_XPYN].angle = 90
        # print('  4444444444444444 ')
        # time.sleep(test_delay)
        # self.motors.servo[MOTOR_CHANNEL.BOTTOM_XPYP].angle = 90
        # print('  55555555555555 ')
        # time.sleep(test_delay)
        # self.motors.servo[MOTOR_CHANNEL.BOTTOM_XNYP].angle = 90
        # print('  666666666666 ')
        # time.sleep(test_delay)
        # self.motors.servo[MOTOR_CHANNEL.BOTTOM_XNYN].angle = 90
        # print('  77777777777777 ')
        # time.sleep(test_delay)
        # self.motors.servo[MOTOR_CHANNEL.BOTTOM_XPYN].angle = 90
        # print('  888888888 ')
        # time.sleep(test_delay)
        print('     Motor as servo is Started.... ')


    def __move_up_down(self, speed):
        '''
        Turn on PWM # 1,2,3,4  at the speed
        '''
        self.my.servo[8].angle = 90
        self.my.servo[9].angle = 90
        self.my.servo[10].angle = 90
        self.my.servo[11].angle = 90
        

    def move_forward(self, speed):
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XNYN].angle = speed
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XPYN].angle = speed
        
    
    def move_backward(self, speed):
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XNYP].angle = speed
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XPYP].angle = speed

    # def move_left(self, speed_clockwise,speed_counterclockwise):
    def move_left(self, speed):
        '''
        Can be 2 motors or 4 motors
        '''
        # self.my.servo[15].angle = speed_clockwise
        # self.my.servo[12].angle = speed_counterclockwise
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XPYN].angle = speed
        self.motors.servo[MOTOR_CHANNEL.BOTTOM_XNYP].angle = speed

    # def move_right(self, speed_clockwise,speed_counterclockwise):
    def move_right(self, speed):
        '''
        Can be 2 motors or 4 motors
        '''
        # '''
        # turn on pwm #6 clockwise
        # turn on PWM #7 counterclockwise
        # '''
        # self.my.servo[13].angle = speed_clockwise
        # self.my.servo[14].angle = speed_counterclockwise
        self.motors[MOTOR_CHANNEL.BOTTOM_XPYN].angle = speed
        self.motors[MOTOR_CHANNEL.BOTTOM_XNYP].angle = speed

    def move_up(self, speed, to_water_depth):
        '''
        turn on pwm #1, #2, #3, #4 clockwise

        move up to a certain depth

        '''
        ServoKit.servo[8].angle = speed
        ServoKit.servo[9].angle = speed
        ServoKit.servo[10].angle = speed
        ServoKit.servo[11].angle = speed

        '''
        self.my.servo[8].angle = speed
        self.my.servo[9].angle = speed
        self.my.servo[10].angle = speed
        self.my.servo[11].angle = speed

        '''
       
        self.__target_water_depth = to_water_depth
        print(to_water_depth)

    def move_down(self, speed ,to_water_depth):
        '''
        turn on pwm #1, #2, #3, #4 counterclockwise

        '''
        self.my.servo[8].angle = speed
        self.my.servo[9].angle = speed
        self.my.servo[10].angle = speed
        self.my.servo[11].angle = speed

        if self.__target_water_depth <= to_water_depth :
            self.my.servo[8].angle = 90
            self.my.servo[9].angle = 90
            self.my.servo[10].angle = 90
            self.my.servo[11].angle = 90 
    
    def turn_left(self, speed_clockwise,speed_counterclockwise):
        '''
        turn on pwm #6 clockwise
        
        turn on PWM #8 counterclockwise

        '''
        self.my.servo[13].angle = speed_clockwise
        self.my.servo[15].angle = speed_counterclockwise
        
    def turn_right(self,speed_clockwise,speed_counterclockwise):
        '''
        turn on pwm #5 clockwise
        
        turn on PWM #7 counterclockwise

        '''
        self.my.servo[12].angle = speed_clockwise
        self.my.servo[14].angle = speed_counterclockwise
    
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
