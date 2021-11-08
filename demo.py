from uwbot import UwBot
from peripheral import SensorsType
from output.propeller import MOVE_DIRECTION

#   Get permission to access UART:
#   sudo chmod 777 /dev/ttyTHS1


def Test(mybot:UwBot):
    mybot.StartAllcameras()
    mybot.StartCamera(1)
    mybot.StopCamera(2)


    
    mybot.Move(MOVE_DIRECTION.FORWARD,100)
    # mybot.__cameres.Stop(6)

    result = mybot.ReadSensor(SensorsType.BATTERY_VOLTATE)
    print("Battery voltage = ", result)

    result = mybot.ReadSensor(SensorsType.WATER_TEMPERATURE)
    print("Water temperature = ", result)

    result = mybot.ReadSensor(SensorsType.DISTANCE_TO_BOTTOM)
    print("Distance to water bottom = ", result)

    result = mybot.ReadSensor(SensorsType.GRAVITY_Z)
    print('Gravity orientation = ', result)




    
  



mybot = UwBot()
todemo = 'unit_test'
# todemo = 'auto_play'

if todemo == 'unit_test':
    Test(mybot)

if todemo == 'auto_play':
    mybot.StartLogger()
    while True:
        mybot.SpinOnce()
