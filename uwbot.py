# from typing_extensions import ParamSpec
from output.propeller import Propeller
from camera.single_camera import SingleCamera
from camera.single_camera import SingleCamera,CameraFactory
from sensor.water_depth_sensor import WaterDepthSensor
from sensor.mpu6050 import Mpu6050

import serial
from serial.serialutil import Timeout

import board
import busio
import smbus

import Adafruit_ADS1x15.ADS1x15 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
# from adafruit_ads1x15.ads1x15 import Mode
# from time import time, sleep


class Direction:
    FORWARD = 1
    BACKWARD = 2
    LEFT = 3
    RIGHT = 4
    UP = 5
    DOWN = 6
    TURN_LEFT = 7
    TURN_RIGHT = 8

class UwBot():
    def __init__(self):
        # Init GPIO
        self.__propeller = Propeller()
        self.cameras = []
        for i in range[1,6]:
            self.cameras.append(CameraFactory.CreateSingleCamera(i))

        pass


    def move(self, direction:Direction, speed:float) :
        '''
        direction list = ['FORWARD', 'BACKWARD']
        speed must in range [0,100]
        '''
        Propeller.__init__(self)
        now_speed_clockwise = 83.55 * ((101 - speed) / 100)
        now_speed_counterclockwise = 180 - 83.55 * ((101 - speed) / 100)
        if direction == Direction.FORWARD:
            self.__propeller.move_forward(now_speed_clockwise)

        elif direction == Direction.BACKWARD:

            self.__propeller.move_backward(now_speed_counterclockwise)

        elif direction == Direction.LEFT:
            self.__propeller.move_left(now_speed_clockwise, now_speed_counterclockwise)

        elif direction == Direction.RIGHT:
            self.__propeller.move_right(now_speed_clockwise, now_speed_counterclockwise)

        elif direction == Direction.UP:
            water_depth = WaterDepthSensor.read_water_depth()
            self.__propeller.move_up(now_speed_clockwise)#, water_depth)

        elif direction == Direction.DOWN:
            water_depth = WaterDepthSensor.read_water_depth()
            print(water_depth)
            self.__propeller.move_down(now_speed_counterclockwise, water_depth)

        elif direction == Direction.TURN_LEFT:
            self.__propeller.turn_left(now_speed_clockwise, now_speed_counterclockwise)

        elif direction == Direction.TURN_RIGHT:
            self.__propeller.turn_right(now_speed_clockwise, now_speed_counterclockwise)
      
    def read_room_humidity(self):
        pass

    def read_room_temperature(self):
        room_temperture = Mpu6050.get_temp()
        return room_temperture

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

    def read_Gavity_orientation (self):
        a_x,a_y,a_z = Mpu6050.get_accel_data()
        g_x,g_y,g_z = Mpu6050.get_gyro_data()
        return a_x,a_y,a_z,g_x,g_y,g_z

    def read_user_button(self):
        pass

    def read_distance_to_bottom(self):
        uart_port = serial.Serial(port= '/dev/ttyTHS1', 
                          baudrate=9600)
        print(uart_port.isOpen())
        data = [0x6f, 0x01, 0x06, 0xd0]
        uart_port.write(data)    
        uart_port.timeout = 1
        received_data = uart_port.readall()   
        distance = received_data[4]*256 + received_data[5]
        return distance

    def read_water_depth(self):
        pass

    def read_battery_voltage(self):
        '''
        range is [0,100]
        '''
        ads1015_address = 0x48
        i2c_bus1 = (busio.I2C(board.SCL_1, board.SDA_1, frequency=100000))
        ads = ADS.ADS1015(i2c_bus1, address=ads1015_address)
        ads1015_channel = AnalogIn(ads, ADS.P1) 
        percent = (1 - (ads1015_channel.voltage - 2.55) / -0.35) * 100
        return percent

    def spin(self):
        while True:
            # voltage = UwBot.read_battery()
            voltage = self.read_battery_voltage()
            if voltage < 20:
                self.__propeller.move_up(20, 0)

    def StartAllcameras(self):
        for i in range (1,6):
            CameraFactory(i)
            SingleCamera.StartPipelineRecording

    def StartCamera(self, camera_id:int) ->None:
        self.cameras[camera_id].StartPipelineRecording()
        test = SingleCamera
        test.StartPipelineRecording


    def StopCamera(self, camera_id:int) -> None:
        self.cameras[camera_id].StopPipelineRecording()

    def FindFish(self, camera_id:int, FishName:str) -> bool:
        pass

    

if __name__ == '__main__':

    pass