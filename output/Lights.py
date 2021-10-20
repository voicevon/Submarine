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

        for index in range(6):
            # GPIO.setup(35, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(self.__pin, GPIO.OUT, initial=GPIO.LOW)

            print(index, 'OK')

    def TurnOnOff(self, onoff:bool) -> None:
        GPIO.output(self.__pin, onoff)

