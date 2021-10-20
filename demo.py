from uwbot import UwBot, Direction


#   sudo chmod 777 /dev/ttyTHS1

mybot =  UwBot()

result = mybot.read_water_temperature()
print("Water temperature = ", result)


result = mybot.read_distance_to_bottom()
print("Distance to water bottom = ", result)

result = mybot.read_Gavity_orientation()
print('Gravity orientation = ', result)

result = mybot.read_battery_voltage()
print("Battery voltage = ", result)



# mybot.StartAllcameras()\
# mybot.StartCamera(1)
# mybot.StopCamera(2)

mybot.move(Direction.FORWARD,100)




# C:
mybot.__cameres.Stop(6)

# UwBot.StartAllcameras()
