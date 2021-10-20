from output.propeller import Propeller
from sensor.water_depth_sensor import WaterDepthSensor

import adafruit_ads1x15.ads1015 as ADS                               
from adafruit_ads1x15.analog_in import AnalogIn
import serial
from serial.serialutil import Timeout

import board
import busio
from output.Lights import InitGPIO, SingleLight


from camera.single_camera import SingleCamera,CameraFactory
  
import adafruit_mpu6050   # https://learn.adafruit.com/mpu6050-6-dof-accelerometer-and-gyro/python-and-circuitpython
import time


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
        print("Unerwater Robot is Initializing......")

        #-----------------------------------------------------------------------
        self.__started_logger = False
        self.__lights = []
        light_pins = [35,33,31,29,19,15]
        InitGPIO()
        for i in range(6):
            new_light = SingleLight(light_pins[i])
            self.__lights.append(new_light)
        print("Uwbot.Init Lights is done...")

        #-----------------------------------------------------------------------
        self.__uart_port = serial.Serial(port= '/dev/ttyTHS1', 
                          baudrate=9600)
        self.__uart_port.timeout = 3
        if self.__uart_port.isOpen():
            print("Uwbot.Init UART is done...")
        else:
            print("  !!!!    !!!!  !!!!   !!!!  Uwbot.Init UART is Failed...")

        #-----------------------------------------------------------------------
        i2c_bus = busio.I2C(board.SCL_1, board.SDA_1, frequency=100000)
        # List I2C device:       
        #   sudo i2cdetect -r -y 0
        print("Uwbot.Init I2C-Bus is done...")

        self.__mpu6050 = adafruit_mpu6050.MPU6050(i2c_bus, address=0x68)
        print("    Uwbot.Init Mpu6050 is done...")

        #-----------------------------------------------------------------------
        ads1015_address = 0x48
        self.__ads1015 = ADS.ADS1015(i2c_bus, address=ads1015_address)
        print("    Uwbot.Init Ads1015 is done...")

        #-----------------------------------------------------------------------
        self.__propeller = Propeller(i2c_bus)
        print("    Uwbot.Init Propeller is done...")


        #-----------------------------------------------------------------------
        print("Uwbot.Creatint cameras")
        myFactory = CameraFactory()
        self.cameras = []
        for i in range(6):
            new_camera = myFactory.CreateSingleCamera(i)
            self.cameras.append(new_camera)
            print("     Uwbot.Create Camera %i  is done..." %i)

        print("Unerwater Robot is Initialized......")

    def move(self, direction:Direction, speed:float) :
        '''
        direction list = ['FORWARD', 'BACKWARD']
        speed must in range [0,100]
        '''
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

    def read_Gavity_orientation (self):
        return self.__mpu6050.acceleration

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
        
    def StartLogger(self):
        self.__started_logger=True

    def SpinOnce(self):
        # voltage = UwBot.read_battery()
        voltage = self.read_battery_voltage()
        if voltage < 20:
            # battery is low, move up to water surface.
            self.__propeller.move_up(20, 0)
        else:
            if self.__started_logger:
                # Write data to influxDB
                pass


if __name__ == '__main__':

    test = UwBot()
    test.test()
