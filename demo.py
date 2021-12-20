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

    while True:
        # print('  ------------------------  ')
        # result = mybot.ReadSensor(SensorsType.WATER_TEMPERATURE)
        # print("Water temperature = ", result)

        # result = mybot.ReadSensor(SensorsType.DISTANCE_TO_BOTTOM)
        # print("Distance to water bottom = ", result)

        # result = mybot.ReadSensor(SensorsType.ROOM_TEMPERATURE)
        # print("Room temperature = ", result)
        
        # result = mybot.ReadSensor(SensorsType.BATTERY_PERCENT)
        # print("Battery voltage = ", result)

        result = mybot.ReadSensor(SensorsType.WATER_DEPTH)
        print("WaterDepth = ", result)



    result = mybot.ReadSensor(SensorsType.GRAVITY_Z)
    print('Gravity orientation = ', result)


def TestLight():
    pass


from output.propeller import MOTOR_CHANNEL
import time

def TestEachPropeller():
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


def TestCombineProperller():
    obj = mybot.peripheral.propeller
    test_speed = 40
    print("Move forward 10 second..")
    obj.move_forward(test_speed)
    time.sleep(10)
    obj.StopAllMotors()
    time.sleep(10)


    print("Move backward 10 second..")
    obj.move_backward(test_speed)
    time.sleep(10)
    obj.StopAllMotors()
    time.sleep(10)


    print("Move move_up 10 second..")
    obj.move_up(test_speed,1)
    time.sleep(10)
    obj.StopAllMotors()
    time.sleep(10)

    print("Move move_down 10 second..")
    obj.move_down(test_speed,1)
    time.sleep(10)
    obj.StopAllMotors()
    time.sleep(10)

    print("Move move_left 10 second..")
    obj.move_left(test_speed)
    time.sleep(10)
    obj.StopAllMotors()
    time.sleep(10)
    
    print("Move move_right 10 second..")
    obj.move_right(test_speed)
    time.sleep(10)
    obj.StopAllMotors()
    time.sleep(10)

    
    print("Move turn_left 10 second..")
    obj.turn_left(test_speed)
    time.sleep(10)
    obj.StopAllMotors()
    time.sleep(10)

    
    print("Move turn_right 10 second..")
    obj.turn_right(test_speed)
    time.sleep(10)
    obj.StopAllMotors()
    time.sleep(10)

  



demo = {"TestSensor":TestSensor,
        "TestLights":TestLight, 
        "TestEachPropeller": TestEachPropeller,
        "TestCombineProperller":TestCombineProperller,
         }
doDemo = demo["TestSensor"]
# doDemo = demo["TestCombineProperller"]
doDemo()



if False:
    mybot.StartLogger()
    while True:
        mybot.SpinOnce()
