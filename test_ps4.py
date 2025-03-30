# from pyPS4Controller.controller import Controller

# class MyController(Controller):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

#     def normalize(self, value):
#         return int((value / 32767) * 100)  

#     def on_L3_left(self, value):
#         print(f"L3 Left: {self.normalize(value)}")

#     def on_L3_right(self, value):
#         print(f"L3 Right: {self.normalize(value)}")

#     def on_L3_up(self, value):
#         print(f"L3 Up: {self.normalize(value)}")

#     def on_L3_down(self, value):
#         print(f"L3 Down: {self.normalize(value)}")
        

#     def on_R3_left(self, value):
#         print(f"R3 Left: {self.normalize(value)}")

#     def on_R3_right(self, value):
#         print(f"R3 Right: {self.normalize(value)}")

#     def on_R3_up(self, value):
#         print(f"R3 Up: {self.normalize(value)}")

#     def on_R3_down(self, value):
#         print(f"R3 Down: {self.normalize(value)}")

#     def on_x_press(self):
#         print("Pressed X")

#     def on_x_release(self):
#         print("Release X")

# controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
# controller.listen()





import threading
import time
from pyPS4Controller.controller import Controller

# Global variable to store the joystick Y-axis value
joystick_y = 0
joystick_lock = threading.Lock()

class MyController(Controller):
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)

    # Update joystick Y-axis value when moving up
    def on_L3_up(self, value):
        global joystick_y
        with joystick_lock:
            joystick_y = value

    # Update joystick Y-axis value when moving down
    def on_L3_down(self, value):
        global joystick_y
        with joystick_lock:
            joystick_y = value

    # Reset Y-axis value to 0 when joystick is released
    def on_L3_y_at_rest(self):
        global joystick_y
        with joystick_lock:
            joystick_y = 0


def joystick_reader():
    """Thread that continuously reads the joystick Y-axis value"""
    prev_y = 0  # Stores the previous Y value
    while True:
        with joystick_lock:
            y = joystick_y  # Read current Y-axis value

        # Print only if value changes or joystick is being held
        if y != prev_y or y != 0:
            print(f"Joystick Y: {y}")
            prev_y = y

        time.sleep(0.05)  # Read at 20 times per second (50ms delay)

# Start a separate thread to continuously read the joystick
reader_thread = threading.Thread(target=joystick_reader, daemon=True)
reader_thread.start()

# Initialize and start listening for controller events
controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen()
