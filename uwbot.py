from peripheral import Peripheral, SensorsType,SensorValue

from camera.single_camera import SingleCamera,CameraFactory


import time




class UwBot():
    def __init__(self):
        print("Unerwater Robot is Initializing......")

        #-----------------------------------------------------------------------
        self.__started_logger = False
        self.__peripheral = Peripheral()
        #-----------------------------------------------------------------------
        print("Uwbot.Creatint cameras")
        myFactory = CameraFactory()
        self.cameras = []
        for i in range(6):
            new_camera = myFactory.CreateSingleCamera(i)
            self.cameras.append(new_camera)
            print("     Uwbot.Create Camera %i  is done..." %i)

        #-----------------------------------------------------------------------
        print("Unerwater Robot is Initialized......")

    def ReadSensor(self, sensor:SensorsType)
        if sensor == SensorsType.BATTERY_VOLTATE:
            return self.__peripheral.read_battery_voltage()
        if sensor == SensorsType.DISTANCE_TO_BOTTOM:
            return self.__peripheral.read_distance_to_bottom()
        if sensor == SensorsType.CAMERA_0:
            return self.cameras[0].state
        if sensor == SensorsType.CAMERA_1:
            return self.cameras[1].state
        if sensor == SensorsType.CAMERA_2:
            return self.cameras[2].state
        if sensor == SensorsType.CAMERA_3:
            return self.cameras[3].state
        if sensor == SensorsType.CAMERA_4:
            return self.cameras[4].state
        if sensor == SensorsType.CAMERA_5:
            return self.cameras[5].state
        if sensor == SensorsType.GRAVITY_X:
            return self.__peripheral.read_Gavity_orientation_x()
        if sensor == SensorsType.GRAVITY_Y:
            return self.__peripheral.read_Gavity_orientation_y()
        if sensor == SensorsType.GRAVITY_Z:
            return self.__peripheral.read_Gavity_orientation_z()
        if sensor == SensorsType.LIGHT_0:
            return self.__peripheral.__lights[0].state
        if sensor == SensorsType.LIGHT_1:
            return self.__peripheral.__lights[1].state
        if sensor == SensorsType.LIGHT_2:
            return self.__peripheral.__lights[2].state
        if sensor == SensorsType.LIGHT_3:
            return self.__peripheral.__lights[3].state
        if sensor == SensorsType.LIGHT_4:
            return self.__peripheral.__lights[4].state
        if sensor == SensorsType.LIGHT_5:
            return self.__peripheral.__lights[5].state

        if sensor == SensorsType.PROPELLER_0_SPEED:
            return self.__peripheral.__propeller.speed[0]
        if sensor == SensorsType.PROPELLER_1_SPEED:
            return self.__peripheral.__propeller.speed[1]
        if sensor == SensorsType.PROPELLER_2_SPEED:
            return self.__peripheral.__propeller.speed[2]
        if sensor == SensorsType.PROPELLER_3_SPEED:
            return self.__peripheral.__propeller.speed[3]
        if sensor == SensorsType.PROPELLER_4_SPEED:
            return self.__peripheral.__propeller.speed[4]
        if sensor == SensorsType.PROPELLER_5_SPEED:
            return self.__peripheral.__propeller.speed[5]
            
      

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
