
import board
import busio
import time

from sensor.water_depth_sensor import WaterDepthSensor
import adafruit_ads1x15.ads1015 as ADS    
#   sudo pip3 install adafruit-circuitpython-ads1x15                      
from adafruit_ads1x15.analog_in import AnalogIn

from output.propeller import Propellers, MOVE_DIRECTION

import serial
from output.Lights import InitGPIO, SingleLight

import adafruit_mpu6050   # https://learn.adafruit.com/mpu6050-6-dof-accelerometer-and-gyro/python-and-circuitpython
#   sudo pip3 install adafruit-circuitpython-mpu6050

class SensorsType:
    BATTERY_VOLTATE = 1
    WATER_TEMPERATURE = 2
    WATER_DEPTH = 3
    DISTANCE_TO_BOTTOM = 4
    GRAVITY_X = 5
    GRAVITY_Y = 6
    GRAVITY_Z = 7
    GRAVITY_XYZ = 101
    LIGHT_0 = 8
    LIGHT_1 = 9
    LIGHT_2 = 10
    LIGHT_3 = 11
    LIGHT_4 = 12
    LIGHT_5 = 13
    CAMERA_0 = 15
    CAMERA_1 = 16
    CAMERA_2 = 17
    CAMERA_3 = 18
    CAMERA_4 = 19
    CAMERA_5 = 20
    PROPELLER_0_SPEED = 21
    PROPELLER_1_SPEED = 22
    PROPELLER_2_SPEED = 23
    PROPELLER_3_SPEED = 24
    PROPELLER_4_SPEED = 25
    PROPELLER_5_SPEED = 26

class SensorValue:
    battery_voltage = 0

    room_temperature = 0
    water_temperature = 0
    depth = 0
    distance_to_bottom = 0
    gravity_x = 0
    gravity_y = 0
    gravity_z = 0

    light_0 = 0
    light_1 = 0
    light_2 = 0
    light_3 = 0
    light_4 = 0
    light_5 = 0
    camera_0 = 0
    camera_1 = 0
    camera_2 = 0
    camera_3 = 0
    camera_4 = 0
    camera_5 = 0


class Peripheral():

    def __init__(self) -> None:
        #-----------------------------------------------------------------------
        i2c_bus = busio.I2C(board.SCL_1, board.SDA_1, frequency=100000)
        # List I2C device:       
        #   sudo i2cdetect -r -y 0
        print("Uwbot.Init I2C-Bus is done...")   

        #-----------------------------------------------------------------------
        self.propeller = Propellers(i2c_bus)
        self.propeller.StartAllMotors()
        print("    Uwbot.Init Propeller is done...")

        self.__mpu6050 = adafruit_mpu6050.MPU6050(i2c_bus, address=0x68)
        print("    Uwbot.Init Mpu6050 is done...")

        #-----------------------------------------------------------------------
        ads1015_address = 0x48
        self.__ads1015 = ADS.ADS1015(i2c_bus, address=ads1015_address)
        print("    Uwbot.Init Ads1015 is done...")

        #-----------------------------------------------------------------------
        self.__uart_port = serial.Serial(port= '/dev/ttyTHS1', baudrate=9600)
        self.__uart_port.timeout = 3
        if self.__uart_port.isOpen():
            print("Uwbot.Init UART is done...")
        else:
            print("  !!!!    !!!!  !!!!   !!!!  Uwbot.Init UART is Failed...")

        #-----------------------------------------------------------------------
        self.__lights = []
        light_pins = [35,33,31,29,19,15]
        InitGPIO()
        for i in range(6):
            new_light = SingleLight(light_pins[i])
            self.__lights.append(new_light)
        print("Uwbot.Init Lights is done...")


    def read_all_sensors(self):
        pass

    def log_to_file(self):
        pass
    def read_room_humidity(self):
        pass

    def read_room_temperature(self):
        return self.__mpu6050.temperature

    def read_water_temperature(self):
        uart_port = serial.Serial(port= '/dev/ttyTHS1', 
                          baudrate=9600)
        print(uart_port.isOpen())
        data = [0x6f, 0x01, 0x06, 0xd0]
        uart_port.write(data)    
        uart_port.timeout = 1
        received_data = uart_port.readall()   
        temperature = received_data[3]
        return temperature

    def read_Gavity_orientation_xyz (self):
        return self.__mpu6050.acceleration

    def read_Gavity_orientation_x (self):
        x,y,z = self.__mpu6050.acceleration
        return x

    def read_Gavity_orientation_y (self):
        x,y,z = self.__mpu6050.acceleration
        return y

    def read_Gavity_orientation_z (self):
        x,y,z = self.__mpu6050.acceleration
        return z
        
    def read_user_button(self):
        pass

    def read_distance_to_bottom(self):

        # command = [0x6f, 0x01, 0x06, 0xd0]
        # self.__uart_port.write(command) 
        # received_data = self.__uart_port.readall() 
        # print(received_data) 
        while True:
            received_data = self.__uart_port.read_all() 
            if received_data.__len__() > 5: 
                distance = received_data[4]*256 + received_data[5]
                return distance
            time.sleep(0.5)
        
    def TurnOnLignt(self,index:int) -> None:
        self.__lights[index].TurnOnOff(True)

    def TurnOffLignt(self,index:int) -> None:
        self.__lights[index].TurnOnOff(False)

    def read_water_temperature(self):
        # command = [0x6f, 0x01, 0x06, 0xd0]
        # self.__uart_port.write(command) 
        while True:
            received_data = self.__uart_port.read_all()  
            if received_data.__len__() > 5: 
                temperature = received_data[3]
                return temperature

    def read_water_depth(self):
        pass

    def read_battery_voltage(self):
        '''
        range is [0,100]
        '''

        ads1015_channel = AnalogIn(self.__ads1015, ADS.P1) 
        percent = (1 - (ads1015_channel.voltage - 2.55) / -0.35) * 100
        return percent

    def test_light(self):
        for t in range(5):
            for i in range(6):
                self.TurnOnLignt(i)
            print("All is on")
            time.sleep(1)

            for i in range(6):
                self.TurnOffLignt(i)
            print ("All is off")
            time.sleep(1)


    def move(self, direction:MOVE_DIRECTION, speed:float) :
        '''
        direction list = ['FORWARD', 'BACKWARD']
        speed must in range [0,100]
        '''
        now_speed_clockwise = 83.55 * ((101 - speed) / 100)
        now_speed_counterclockwise = 180 - 83.55 * ((101 - speed) / 100)
        if direction == MOVE_DIRECTION.FORWARD:
            self.propeller.move_forward(now_speed_clockwise)

        elif direction == MOVE_DIRECTION.BACKWARD:

            self.propeller.move_backward(now_speed_counterclockwise)

        elif direction == MOVE_DIRECTION.LEFT:
            self.propeller.move_left(now_speed_clockwise, now_speed_counterclockwise)

        elif direction == MOVE_DIRECTION.RIGHT:
            self.propeller.move_right(now_speed_clockwise, now_speed_counterclockwise)

        elif direction == MOVE_DIRECTION.UP:
            water_depth = WaterDepthSensor.read_water_depth()
            self.propeller.move_up(now_speed_clockwise)#, water_depth)

        elif direction == MOVE_DIRECTION.DOWN:
            water_depth = WaterDepthSensor.read_water_depth()
            print(water_depth)
            self.propeller.move_down(now_speed_counterclockwise, water_depth)

        elif direction == MOVE_DIRECTION.TURN_LEFT:
            self.propeller.turn_left(now_speed_clockwise, now_speed_counterclockwise)

        elif direction == MOVE_DIRECTION.TURN_RIGHT:
            self.propeller.turn_right(now_speed_clockwise, now_speed_counterclockwise)     



if __name__ == '__main__':

    obj = Peripheral()
    

