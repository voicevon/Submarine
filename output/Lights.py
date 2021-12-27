import Jetson.GPIO as GPIO
#  Jetson Expansion Header Tool
#       sudo /opt/nvidia/jetson-io/jetson-io.py
#           from: https://www.jetsonhacks.com/2020/05/04/spi-on-jetson-using-jetson-io/


def InitGPIO():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)


class LIGHT_PIN:
    PIN_LIGHT_TOP = 15
    PIN_LIGHT_BOTTOM = 19
    PIN_LIGHT_LEFT = 29
    PIN_LIGHT_RIGHT = 31
    PIN_LIGHT_FRONT =33
    PIN_LIGHT_REAR = 35

class LIGHT_INDEX:
    INDEX_LIGHT_TOP = 0
    INDEX_LIGHT_BOTTOM = 1
    INDEX_LIGHT_LEFT = 2
    INDEX_LIGHT_RIGHT = 3
    INDEX_LIGHT_FRONT = 4
    INDEX_LIGHT_REAR = 5

    
class SingleLight:

    def __init__(self, pin) -> None:
        self.__pin = pin
        GPIO.setup(self.__pin, GPIO.OUT, initial=GPIO.LOW)
        self.state = 0 # 0 is off,  1 is on
        print('      SingleLight is created. on GPIO: ', pin )

    def TurnOnOff(self, onoff:bool) -> None:
        GPIO.output(self.__pin, onoff)
        self.state = onoff

