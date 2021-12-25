from sensor.water_depth_sensor import WaterDepthSensor
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
        # pwm_controller_address = 0x40
        self.MIDDLE_CYCLE = 4800
        self.cycle_per_degree = 32
        self.pca = PCA9685(i2c_bus)
        self.pca.frequency = 50
        #self.pca.channels[MOTOR_CHANNEL.TOP_XNYN].duty_cycle = 0x7FFF
        time.sleep(1)
        # self.pca.channels[MOTOR_CHANNEL.TOP_XNYN].duty_cycle = 0x3FFF

    def StartSingleMotor(self, channel_id:int):
        print("  Starting Motor  -------------------", channel_id)
        self.pca.channels[channel_id].duty_cycle = self.MIDDLE_CYCLE
        # time.sleep(1)
        # self.pca.channels[channel_id].duty_cycle = self.MIDDLE_CYCLE
    

    def TestSingleMotor(self,channel_id:int):
        # max = 8000
        # min = 1600
        # # step = 500
        # step = max-min -1
        # print("++++++++++++++++++++++++++++++++++++++")
        # for i in range(min,max,step):
        #     self.pca.channels[channel_id].duty_cycle = i
        #     print (i)
        #     time.sleep(2)

        # for i in range(max,min,-step):
        #     self.pca.channels[channel_id].duty_cycle = i
        #     print(i)
        #     time.sleep(2)



        print("   Runing CW  10 seconds  -----------------", channel_id)
        self.pca.channels[channel_id].duty_cycle = int( self.MIDDLE_CYCLE + self.cycle_per_degree * 25)
        time.sleep(2)
        print("       Sleeping  10 seconds   ")
        self.pca.channels[channel_id].duty_cycle = self.MIDDLE_CYCLE

        time.sleep(2)


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
        self.my.servo[8].duty_cycle = 90
        self.my.servo[9].duty_cycle = 90
        self.my.servo[10].angle = 90
        self.my.servo[11].angle = 90
        
    def _GetDutyCircle(self, speed) ->int:
        return 360 * speed

    def move_forward(self, speed):
        speed = self._GetDutyCircle(speed)
        self.pca.channels[MOTOR_CHANNEL.BOTTOM_XNYN].duty_cycle = self.MIDDLE_CYCLE - speed 
        self.pca.channels[MOTOR_CHANNEL.BOTTOM_XPYN].duty_cycle = self.MIDDLE_CYCLE - speed 
        
    
    def move_backward(self, speed):
        speed = self._GetDutyCircle(speed)
        self.pca.channels[MOTOR_CHANNEL.BOTTOM_XNYP].duty_cycle = self.MIDDLE_CYCLE + speed
        self.pca.channels[MOTOR_CHANNEL.BOTTOM_XPYP].duty_cycle = self.MIDDLE_CYCLE + speed

    # def move_left(self, speed_clockwise,speed_counterclockwise):
    def move_left(self, speed):
        '''
        Can be 2 motors or 4 motors, We choose 2 motors.
        '''
        speed = self._GetDutyCircle(speed)
        self.pca.channels[MOTOR_CHANNEL.BOTTOM_XPYN].duty_cycle = self.MIDDLE_CYCLE + speed
        self.pca.channels[MOTOR_CHANNEL.BOTTOM_XPYP].duty_cycle = self.MIDDLE_CYCLE - speed

    def move_right(self, speed):
        '''
        Can be 2 motors or 4 motors
        '''
        speed = self._GetDutyCircle(speed)
        self.pca.channels[MOTOR_CHANNEL.BOTTOM_XNYN].duty_cycle = self.MIDDLE_CYCLE + speed
        self.pca.channels[MOTOR_CHANNEL.BOTTOM_XNYP].duty_cycle = self.MIDDLE_CYCLE - speed

    def move_up(self, speed, to_water_depth):
        speed = self._GetDutyCircle(speed)
        self.pca.channels[MOTOR_CHANNEL.TOP_XPYP].duty_cycle = self.MIDDLE_CYCLE + speed
        self.pca.channels[MOTOR_CHANNEL.TOP_XNYP].duty_cycle = self.MIDDLE_CYCLE + speed
        self.pca.channels[MOTOR_CHANNEL.TOP_XNYN].duty_cycle = self.MIDDLE_CYCLE + speed
        self.pca.channels[MOTOR_CHANNEL.TOP_XPYN].duty_cycle = self.MIDDLE_CYCLE + speed


    def move_down(self, speed ,to_water_depth):
        speed = self._GetDutyCircle(speed)
        self.pca.channels[MOTOR_CHANNEL.TOP_XPYP].duty_cycle = self.MIDDLE_CYCLE - speed
        self.pca.channels[MOTOR_CHANNEL.TOP_XNYP].duty_cycle = self.MIDDLE_CYCLE - speed
        self.pca.channels[MOTOR_CHANNEL.TOP_XNYN].duty_cycle = self.MIDDLE_CYCLE - speed
        self.pca.channels[MOTOR_CHANNEL.TOP_XPYN].duty_cycle = self.MIDDLE_CYCLE - speed
    
    def turn_left(self, speed:int):
        speed = self._GetDutyCircle(speed)
        self.pca.channels[MOTOR_CHANNEL.BOTTOM_XPYP].anduty_cyclegle = self.MIDDLE_CYCLE - speed
        self.pca.channels[MOTOR_CHANNEL.BOTTOM_XNYN].duty_cycle = self.MIDDLE_CYCLE + speed

    def turn_right(self,speed:int) -> None:
        speed = self._GetDutyCircle(speed)
        self.pca.channels[MOTOR_CHANNEL.BOTTOM_XPYP].duty_cycle = self.MIDDLE_CYCLE + speed
        self.pca.channels[MOTOR_CHANNEL.BOTTOM_XNYN].duty_cycle = self.MIDDLE_CYCLE - speed
    
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
