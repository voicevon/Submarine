from uwbot import UwBot
from peripheral import SensorsType
from output.propeller import MOVE_DIRECTION

#   Get permission to access UART:
#   sudo chmod 777 /dev/ttyTHS1

mybot = UwBot()

def TestSensor():
    # mybot.StartAllcameras()
    # mybot.StartCamera(1)
    # mybot.StopCamera(2)
    
    # mybot.Move(MOVE_DIRECTION.FORWARD,100)
    # mybot.__cameres.Stop(6)

    result = mybot.ReadSensor(SensorsType.BATTERY_VOLTATE)
    print("Battery voltage = ", result)

    while True:
        print('  ------------------------  ')
        result = mybot.ReadSensor(SensorsType.WATER_TEMPERATURE)
        print("Water temperature = ", result)

        result = mybot.ReadSensor(SensorsType.DISTANCE_TO_BOTTOM)
        print("Distance to water bottom = ", result)

        result = mybot.ReadSensor(SensorsType.ROOM_TEMPERATURE)
        print("Room temperature = ", result)


    result = mybot.ReadSensor(SensorsType.GRAVITY_Z)
    print('Gravity orientation = ', result)


def TestLight():
    pass

def TestPropeller():
    pass

    
  



demo = {"TestSensor": TestSensor, "TestLights":TestLight, "TestProperllers": TestPropeller }
f = demo["TestSensor"]
f()



if False:
    mybot.StartLogger()
    while True:
        mybot.SpinOnce()
