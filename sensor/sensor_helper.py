class SensorValue:
    battery_voltage = 0

    room_temperature = 0
    water_temperature = 0
    depth = 0
    distance_to_bottom = 0
    gravity_x = 0
    gravity_y = 0
    gravity_z = 0
    lighte_0 = 0
    lighte_1 = 0
    lighte_2 = 0
    lighte_3 = 0
    lighte_4 = 0
    lighte_5 = 0
    camera_0 = 0
    camera_1 = 0
    camera_2 = 0
    camera_3 = 0
    camera_4 = 0
    camera_5 = 0


class SensorHelper:
    def __init__(self) -> None:
        pass

    def read_all_sensors(self):
        pass

    def log_to_file(self):
        pass
