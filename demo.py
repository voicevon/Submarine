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


from output.propeller import MOTOR_CHANNEL

def TestPropeller():
    print("Testing TOP_XPYP")
    mybot.peripheral.propeller.TestSingleMotor(MOTOR_CHANNEL.TOP_XPYP)
    print("Testing TOP_XNYP")
    mybot.peripheral.propeller.TestSingleMotor(MOTOR_CHANNEL.TOP_XNYP)
    print("Testing TOP_XNYN")
    mybot.peripheral.propeller.TestSingleMotor(MOTOR_CHANNEL.TOP_XNYN)
    print("Testing TOP_XPYN")
    mybot.peripheral.propeller.TestSingleMotor(MOTOR_CHANNEL.TOP_XPYN)
    print("Testing BOTTOM_XPYP")
    mybot.peripheral.propeller.TestSingleMotor(MOTOR_CHANNEL.BOTTOM_XPYP)
    print("Testing BOTTOM_XNYP")
    mybot.peripheral.propeller.TestSingleMotor(MOTOR_CHANNEL.BOTTOM_XNYP)
    print("Testing BOTTOM_XNYN")
    mybot.peripheral.propeller.TestSingleMotor(MOTOR_CHANNEL.BOTTOM_XNYN)
    print("Testing BOTTOM_XPYN")
    mybot.peripheral.propeller.TestSingleMotor(MOTOR_CHANNEL.BOTTOM_XPYN)

    


    
  



demo = {"TestSensor": TestSensor, "TestLights":TestLight, "TestProperllers": TestPropeller }
# f = demo["TestSensor"]
doDemo = demo["TestProperllers"]
doDemo()



if False:
    mybot.StartLogger()
    while True:
        mybot.SpinOnce()
