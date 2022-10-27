"""
@author: Abdelrahman Mahmoud Gaber
@email: abdulrahman.mahmoud1995@gmail.com

@author: Atiqah Liyana
@email: atiqahliyana.work@gmail.com
"""

from serial_communication2 import *
from commands2 import *

"""
TODO:
    1. create the listener thread
    2. AT-COMMAND reader Class 
    3. 

"""

class Lora(SerialCommunication):
    def __init__(self, port, baudrate, timeout=1, debug=True):
        super().__init__(port, baudrate, timeout, debug)

        self._sending_timeout = timeout
        self._status = StatusNetwork.RESET # defualt 
    
    @property
    def status(self):
        return self._status

    def send_raw_command(self, command):
        """
        Send raw command to the LoRa module.

        param: command: str
        """
        # TODO
        #   1. stop the thread from reading the coming data .. 
        # clear all coming data if any
        command = command.serilize().encode()
        # timer = time.time()
        while self.is_available:
            # for debugging
            print("----------FOUND IN BUFFER------------")
            print(self.readlines())
            print("-------------------------------------")
            # if time.time() - timer > self._sending_timeout:
            #     raise Exception("Couldn't clear the buffer")
        self.send(command)
        return 



# lora = Lora("/dev/ttyUSB2", 9600, timeout=0.1)
# lora = Lora("/dev/ttyUSB0", 9600, timeout=0.1)
# lora.connect()
# lrsend = Command("LRSEND", SET, port=33, confirm=0, len=33, data="<abcdef")
# status = Command("STATUS", GET)
# devinfo = Command("DEVINFO", GET)

# appeui = Command("APPEUI", GET) #(atiqah) 

# lora.send_raw_command(devinfo)
# lora.send_raw_command(status)
# lora.send_raw_command(lrsend)

# print(appeui.serilize())
# lora.send_raw_command(appeui.serilize()) #(atiqah)
# time.sleep(0.1)
# lora.send_raw_command(appeui) 
"""
TO DO: 
    Display data without \r\n
"""
# print("coming data: ",  lora.is_available)
# data = lora.readlines()
# print(data)

# n, m, p = Command.command_check(b'+DEVINFO:"M100C  FW VER:0.99.78  HW VER:1.01(H)  BOOT VER:0.99.14  LORAWAN VER:1.0.2  REGION:AS923"\r\n'.decode().strip())
# dev_info = Command.construct_from_payload(n, m, p)
# print(vars(dev_info))
# dev_info.info
