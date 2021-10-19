from uwbot import UwBot, Direction


mybot =  UwBot()

# UwBot.move(Direction.FORWARD,20)
mybot.move(Direction.TURN_RIGHT)

# A:
# mybot.StartAllcameras()\

# B:
mybot.StartCamera(1)
mybot.StopCamera(2)


# C:


mybot.__cameres.Stop(6)

# UwBot.StartAllcameras()
