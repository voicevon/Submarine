from uwbot import UwBot, Direction


mybot =  UwBot()

result = mybot.read_Gavity_orientation()
print('Gravity orientation = ', result)

result = mybot.read_battery_voltage()
print("Battery voltage = ", result)

result = mybot.read_distance_to_bottom()
print("Distance to water bottom = ", result)

# mybot.StartAllcameras()\
# mybot.StartCamera(1)
# mybot.StopCamera(2)

mybot.move(Direction.FORWARD)




# C:
mybot.__cameres.Stop(6)

# UwBot.StartAllcameras()
