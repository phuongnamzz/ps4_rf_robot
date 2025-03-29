
from pyrf24 import RF24, RF24_PA_MAX,RF24_250KBPS

class RFComm:
    def __init__(self, ce_pin=22, csn_pin=0, address=b"00009", role="TX"):
        """ 
        """
        self.radio = RF24(ce_pin, csn_pin)
        if not self.radio.begin():
            raise RuntimeError("❌ NRF24 initialization failed!")

        self.radio.setPALevel(RF24_PA_MAX)
        self.radio.setDataRate(RF24_250KBPS)
        self.radio.setRetries(5, 15)
        self.address = address
        self.role = role.upper()

        if self.role == "TX":
            self.radio.openWritingPipe(self.address)
            self.radio.stopListening()
        elif self.role == "RX":
            self.radio.openReadingPipe(0, self.address)
            self.radio.startListening()
        else:
            raise ValueError("❌ Role must be 'TX' or 'RX'")

    def send(self, message: str):
        """ 
        """
        if self.role != "TX":
            raise RuntimeError("❌ This module is in RX mode, cannot send!")

        msg_bytes = message.encode()
        print(f"📡 Sending: {message}")

        if self.radio.write(msg_bytes):
            print("✅ Sent successfully!")
            return True
        else:
            print("❌ Send failed!")
            return False

    def receive(self):
        """ 
        """
        if self.role != "RX":
            raise RuntimeError("❌ This module is in TX mode, cannot receive!")

        if self.radio.available():
            received_msg = bytearray(32)
            self.radio.read(received_msg, len(received_msg))
            message = received_msg.decode().strip("\x00")
            print(f"📥 Received: {message}")
            return message
        return None



"""
move(left_motor_speed, right_motor_speed): dieu khien doc lap tung banh xe
move(speed): dieu khien 2 banh xe tien lui
rotate(speed): dk xoay trai phai
toggle_weapon(value): bat/tat vu khi

minh thong nhat speed: -100 / 0 / 100
weapon value chac 0 / 1 hoac 0 / 100
"""


class RobotControl:
    # def __init__(self, left_motor: True, right_motor: True, weapon : True, rf_comm: RFComm):
    def __init__(self,  rf_comm: RFComm):
        """ """
        # self.lef_motor = left_motor
        # self.right_motor = right_motor
        # self.weapon = weapon
        self.rf_comm = rf_comm

    def _validate_speed(self, speed: int) -> bool:
        """ """
        return -100 <= speed <= 100

    def move(self, left_speed: int, right_speed: int = None):
        """ Move the robot with one or two speed values. """
        if right_speed is None:  # If only one speed is given, apply it to both wheels
            right_speed = left_speed

        if not self._validate_speed(left_speed) or not self._validate_speed(right_speed):
            return

        command = f"move({left_speed},{right_speed})"
        self.rf_comm.send(command)


    def rotate(self, speed: int):
        """ """
        if not self._validate_speed(speed):
            return
        command = f"rotate({speed})"
        self.rf_comm.send(command)

    def toggle_weapon(self, value: bool):
        if isinstance(value, bool):
            return
        command = f"toggle_weapon({value})"
        self.rf_comm.send(command)
