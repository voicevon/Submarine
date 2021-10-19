from sensor.water_depth_sensor import WaterDepthSensor
from  adafruit_servokit import ServoKit
from adafruit_pca9685 import PCA9685

# import board
import busio


class Propeller():
    '''
    Manage PWM output
    Upper layer will never know what is PWM, channel.

    '''

    def __init__(self, i2c_bus: busio.I2C):
        # init PCA9685
        pwm_controller_address = 0x40
        # i2c_bus0=(busio.I2C(board.SCL_1,board.SDA_1,frequency=400000))
        ServoKit(channels=16, i2c=i2c_bus, address=pwm_controller_address, frequency=49.5)


    def move_forward(self, speed):
        '''
        turn on PWM #7, #8 clockwise

        '''
        self.my.servo[14].angle = speed
        self.my.servo[15].angle = speed
        
    
    def move_backward(self, speed):
        '''
        turn on PWM #5, #6 counterclockwise

        '''
        self.my.servo[12].angle = speed
        self.my.servo[13].angle = speed

    def move_left(self, speed_clockwise,speed_counterclockwise):
        '''
        turn on pwm #8 clockwise

        turn on PWM #5 counterclockwise

        '''
        self.my.servo[15].angle = speed_clockwise
        self.my.servo[12].angle = speed_counterclockwise

        pass

    def move_right(self, speed_clockwise,speed_counterclockwise):
        '''
        turn on pwm #6 clockwise
        
        turn on PWM #7 counterclockwise

        '''
        self.my.servo[13].angle = speed_clockwise
        self.my.servo[14].angle = speed_counterclockwise
        pass
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
    
    def __move_up_down(self, speed):
        '''
        Turn on PWM # 1,2,3,4  at the speed
        '''

        self.my.servo[8].angle = 90
        self.my.servo[9].angle = 90
        self.my.servo[10].angle = 90
        self.my.servo[11].angle = 90
        

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
