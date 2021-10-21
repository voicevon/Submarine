from uwbot import UwBot
from peripheral import SensorsType
from output.propeller import Direction


#   sudo chmod 777 /dev/ttyTHS1


def Test(mybot):
    result = mybot.ReadSensor(SensorsType.BATTERY_VOLTATE)
    print("Battery voltage = ", result)

    result = mybot.ReadSensor(SensorsType.WATER_TEMPERATURE)
    print("Water temperature = ", result)

    result = mybot.ReadSensor(SensorsType.DISTANCE_TO_BOTTOM)
    print("Distance to water bottom = ", result)

    result = mybot.ReadSensor(SensorsType.GRAVITY_Z)
    print('Gravity orientation = ', result)


    mybot.StartAllcameras()
    mybot.StartCamera(1)
    mybot.StopCamera(2)

    mybot.move(Direction.FORWARD,100)
    mybot.__cameres.Stop(6)
    




mybot = UwBot()
Test(mybot)

# mybot.StartLogger()
# while True:
#     mybot.SpinOnce()
