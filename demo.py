from uwbot import UwBot, Direction


#   sudo chmod 777 /dev/ttyTHS1
class App:
    def __init__(self) -> None:
        self.mybot =  UwBot()

    def Test(self):
        result = self.mybot.read_water_temperature()
        print("Water temperature = ", result)

        result = self.mybot.read_distance_to_bottom()
        print("Distance to water bottom = ", result)

        result = self.mybot.read_Gavity_orientation()
        print('Gravity orientation = ', result)

        result = self.mybot.read_battery_voltage()
        print("Battery voltage = ", result)

        self.mybot.StartAllcameras()
        self.mybot.StartCamera(1)
        self.mybot.StopCamera(2)

        self.mybot.move(Direction.FORWARD,100)
        self.mybot.__cameres.Stop(6)
    
    def Spin(self):
        self.mybot.StartLogger()
        while True:
            self.mybot.SpinOnce()


if __name__== "__MAIN__":
    myApp = App()
    # myApp.Test()
    
    myApp.Spin()


# C:

# UwBot.StartAllcameras()
