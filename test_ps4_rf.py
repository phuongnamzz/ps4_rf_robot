# from pyPS4Controller.controller import Controller
# from Robot_control import RobotControl
# from Robot_control import RFComm


# rf24 = RFComm()
# robot = RobotControl(rf24)  

# class MyController(Controller):
#     def __init__(self, robot, **kwargs):
#         super().__init__(**kwargs)
#         self.robot = robot  

#     def normalize(self, value):
#         return int((value / 32767) * 100)  

#     def on_L3_left(self, value):
#         speed = self.normalize(value)
#         print(f"L3 Left: {speed}")
#         self.robot.move(speed, speed)  
#         print("send speed over RF")

#     def on_L3_right(self, value):
#         speed = self.normalize(value)
#         print(f"L3 Right: {speed}")
#         self.robot.move(speed, speed)
#         print("send speed over RF")

#     def on_L3_up(self, value):
#         speed = self.normalize(value)
#         print(f"L3 Up: {speed}")
#         self.robot.move(speed, speed)
#         print("send speed over RF")

#     def on_L3_down(self, value):
#         speed = self.normalize(value)
#         print(f"L3 Down: {speed}")
#         self.robot.move(speed, speed)
#         print("send speed over RF")

#     def on_x_press(self):
#         print("Pressed X")

#     def on_x_release(self):
#         print("Released X")


# controller = MyController(robot, interface="/dev/input/js0", connecting_using_ds4drv=False)
# controller.listen()




from Robot_control import RobotControl, RFComm
import threading
import time
from pyPS4Controller.controller import Controller

# Initialize robot control
rf24 = RFComm()
robot = RobotControl(rf24)

# Global variables to store joystick Y-axis values
joystick_L3_y = 0
joystick_R3_y = 0
joystick_lock = threading.Lock()

class MyController(Controller):
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        self.robot = robot

    # Normalize joystick values (-32767 to 32767) into (-100 to 100)
    def normalize(self, value):
        return int((value / 32767) * 100)

    # Update L3 Y-axis value when moving up or down (invert the value)
    def on_L3_up(self, value):
        global joystick_L3_y
        with joystick_lock:
            joystick_L3_y = -self.normalize(value)  # Invert value

    def on_L3_down(self, value):
        global joystick_L3_y
        with joystick_lock:
            joystick_L3_y = -self.normalize(value)  # Invert value

    # Reset L3 Y-axis value when joystick is released
    def on_L3_y_at_rest(self):
        global joystick_L3_y
        with joystick_lock:
            joystick_L3_y = 0

    # Update R3 Y-axis value when moving up or down (invert the value)
    def on_R3_up(self, value):
        global joystick_R3_y
        with joystick_lock:
            joystick_R3_y = -self.normalize(value)  # Invert value

    def on_R3_down(self, value):
        global joystick_R3_y
        with joystick_lock:
            joystick_R3_y = -self.normalize(value)  # Invert value

    # Reset R3 Y-axis value when joystick is released
    def on_R3_y_at_rest(self):
        global joystick_R3_y
        with joystick_lock:
            joystick_R3_y = 0

def joystick_reader():
    """Thread that continuously reads joystick values and sends commands"""
    prev_L3_y = 0  # Previous L3 Y-axis value
    prev_R3_y = 0  # Previous R3 Y-axis value

    while True:
        with joystick_lock:
            L3_y = joystick_L3_y  # Read L3 Y-axis
            R3_y = joystick_R3_y  # Read R3 Y-axis

        # Only send commands if values change or joystick is being held
        if L3_y != prev_L3_y or R3_y != prev_R3_y or L3_y != 0 or R3_y != 0:
            print(f"Joystick L3 Y: {L3_y}, Joystick R3 Y: {R3_y}")
            robot.move(L3_y, R3_y)  # Send command to robot
            prev_L3_y = L3_y
            prev_R3_y = R3_y

        time.sleep(0.05)  # Read at 20 times per second (50ms delay)

# Start a separate thread to continuously read joystick values
reader_thread = threading.Thread(target=joystick_reader, daemon=True)
reader_thread.start()

# Initialize and start listening for controller events
controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen()
