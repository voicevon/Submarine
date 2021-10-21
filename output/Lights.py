import Jetson.GPIO as GPIO
#  Jetson Expansion Header Tool
#       sudo /opt/nvidia/jetson-io/jetson-io.py
#           from: https://www.jetsonhacks.com/2020/05/04/spi-on-jetson-using-jetson-io/


def InitGPIO():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)

class SingleLight:

    def __init__(self, pin) -> None:
        self.__pin = pin
        GPIO.setup(self.__pin, GPIO.OUT, initial=GPIO.LOW)
        self.state = 0 # 0 is off,  1 is on
        print('      SingleLight is created. on GPIO: ', pin )

    def TurnOnOff(self, onoff:bool) -> None:
        GPIO.output(self.__pin, onoff)
        self.state = onoff

