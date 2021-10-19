import serial
from serial.serialutil import Timeout
#uart = busio.UART(board.TX,board.RX , baudrate=9600)

uart_port = serial.Serial(port= '/dev/ttyTHS1', 
                          baudrate=9600)
# uart_port = serial.Serial(port= '/dev/ttyTHS1',baudrate=115200)
print(uart_port.isOpen())


data = [0x6f, 0x01, 0x06, 0xd0]
uart_port.write(data)
print("written")
# us_r = serial.Serial(port='/dev/ttyTHS1',baudrate=9600)

uart_port.timeout = 1
received_data = uart_port.readall()
print(received_data)

received_data = bytes([0x6a, 0x01,0x06,0x1b,0x0A,0XF0,0x11,0x00,0XDF])
print("the temperature is",received_data[3])
distance = received_data[4]*256 + received_data[5]


print("the distance is ",distance , 'mm')

