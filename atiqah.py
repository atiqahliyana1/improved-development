#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 10:06:02 2022
@author: Abdelrahman Mahmoud Gaber
@email: abdulrahman.mahmoud1995@gmail.com

@author: Atiqah Liyana
@email: atiqahliyana.work@gmail.com

"""

from enum import IntEnum #from m300h.py and #from commands2.py
from serial import Serial, SerialException, SerialTimeoutException #from serial_communication2.py
from message import * #from commands2.py
import time #from serial_communication2.py
import re #from commands2.py

# import sys #dependencies on OS system plugged in
# import glob #dependencies on global

# combination of m300h.py, serial_communication2.py, lora2.py, commands2.py

# --------from m300h.py-------start-------------- 
# command types 
SET = 0
GET = 1
EXECUTE = 2
REPORT = 3 # ^X:P report command, P is the parameter e.g. '^LRRECV:1,22,-44,29,2,<ABCD,923.2,2\r\n'

SET_STR = "="
GET_STR = "=?"
EXECUTE_STR = ""
REPORT_STR = ""

CR = "\r"
LF = "\n"
CRLF = "\r\n"

AT_CMD_PREFIX = "AT+"

COMMAND_REGEX = r"(?:\^|\+)([A-Z0-9]*):" # command regex to check if data contains a command

AT_COMMANDS = {  # definations for query and set 

    "LRSEND" : ( 
        ("port"   , int),
        ("confirm", int),
        ("len"    , int),
        ("data"   , str) # TODO: convert to bytes
    ),

    "LRNSEND" : ( # port, confirm, nbtrials, len, data
        ("port"    , int),
        ("confirm" , int),
        ("nbtrials", int),
        ("len"     , int),
        ("data"    , str) # TODO: convert to bytes
    ),

    "DEVINFO" : (
        ("info", str),
    ),

    "REGION" : ( 
        ("region", int),
    ),

    "DEVCLASS": (
        ("class", int),
    ),
    
    "STATUS": (
        ("status", int),
    ),

    "ACTIVEMODE": (
        ("mode", int),
    ),
    
    "APPEUI": (
        ("eui", str)
    ),

}

AT_COMMANDS_REPORT = {
    "LRSEND": (
        ("seq"    , int),
        ("port"   , int),
        ("confirm", int),
        ("len"    , int),
        ("freq"   , float),
        ("dr"     , int)
    ),

    "LRRECV": (
        ("seq" , int),
        ("port", int),
        ("rssi", int),
        ("snr" , int),
        ("len" , int),
        ("data", str),
        ("freq", float),
        ("dr"  , int)
    ),

    "LRCONFIRM": ( # seq, rssi, snr, freq, dr
        ("seq" , int),
        ("rssi", int),
        ("snr" , int),
        ("freq", float),
        ("dr"  , int)
    ),

    "LRJOIN": (
        ("freq", float),
        ("dr"  , int),
    ),

    "STATUS": ( 
        ("status", int),
    ),
    
    "APPEUI": ( 
        ("eui", int),
    ),
}

# status network enum
class StatusNetwork(IntEnum):
    RESET = 0
    P2P_NETWORK = 1
    NOT_JOINED = 2
    OTAA_JOINED = 3
    ABP_JOINED = 4

class DevClass(IntEnum):
    CLASS_A = 0
    CLASS_B = 1
    CLASS_C = 2

class DevClassStatus(IntEnum):
    OK = 0
    ERROR = 1

class ActiveMode(IntEnum):
    OTAA = 0
    ABP = 1 # gps detected 
    OTAA_RPM = 2 

StatusMsg = {
    0: "Reset",
    1: 'In the P2P communication state',
    2: 'In the LORAWAN state is not joined to the network',
    3: "In LORAWAN OTAA mode and already in the network status",
    4: "In LORAWAN ABP mode and already in the network status"
}

ErrorMsg = {
    1 : "The number of AT command characters exceeds the range",
    2 : "Unknown command that is not recognized",
    3 : "The command is not allowed to be executed",
    4 : "Parameter format or type error",
    5 : "The parameter is out of range",
    6 : "The length of the block parameter or string parameter exceeds the range",
    7 : "The LORAWAN data send queue is full",
    10 : "The module is not activated"
}

class CommandNotFoundError(Exception):
    """
    Exception for when a command is not found or defined in AT commands
    """
    pass

class CommandError(Exception):
    """
    command is not properly formatted or defined or has invalid fields
    """
    pass
# ----------------from m300h.py------------end----------------#

# --------from serial_communication2.py------start------------#

class SerialCommunication:  
    """
    def portcheck(self): 
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        else: 
            raise EnvironmentError('Unsupported platform')
        
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result
    """

    def __init__(self, port, baudrate, timeout=1, debug=True):
        self._serial_object = None
        self._connected = False
        self._reading = False
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._debug = debug

    def __del__(self):

        self.disconnect()

    def connect(self):
        """
        Open serial connection.
        """

        self._connected = False
        try:
            self._serial_object = Serial(
                self._port, self._baudrate, timeout=self._timeout
            )

            self._connected = True
            if self._debug:
                print("INFO: Connected Successfully to port: {}".format(self._port))
            
        except (SerialException, SerialTimeoutException) as err:
            print(f"Error connecting to serial port {err}")

        return self._connected

    def disconnect(self):
        """
        Close serial connection.
        """

        if self._connected and self._serial_object:
            try:
                self._serial_object.close()
            except (SerialException, SerialTimeoutException) as err:
                print(f"Error disconnecting from serial port {err}")
        self._connected = False

        return self._connected

    def send(self, data):
        """
        Send data to serial connection.
        """

        self._serial_object.write(data)

    def flush(self):
        """
        Flush input buffer
        """

        self._serial_object.reset_input_buffer()
    
    def read(self, size=1):
        """
        Read bytes(size) from serial connection.
        """

        return self._serial_object.read(size)

    def readline(self):
        """
        Read line from serial connection.
        """

        return self._serial_object.readline()
    
    def readlines(self):
        """
        Read a list of recived lines from serial connection.
        """
        
        # return [line.decode() for line in self._serial_object.readlines()]
        return self._serial_object.readlines()

    @property
    def is_available(self):
        """
        Check if any messages remaining in the input buffer
        """

        return self._serial_object.in_waiting

# --------from serial_communication2.py------end----

#---------from lora2.py-----------------
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
#---------from lora2.py-----------------end---------

#---------from commands2.py-------------start-------
class Command:
       
    def __init__(self, name, mode=GET, **kwargs):
        """
        Constructor for AT Commands that user can send. 
        
        .. NOTE::
            This constructor valid only(to set attributes) for GET, SET, EXECUTE commands.
            REPORT however will have a special method to handle it. 
        
        :param name: name of the command (for example: LRSEND, LRCONFIRM)
        :param mode: command mode e.g. GET, SET, EXECUTE  or REPORT
        :param kwargs: if command fields need to be added for example(port=12, seq=365, and so on)
        """
        self.name = name # command name
        self._payload = ""
        self._mode = mode
        self._mode_str = GET_STR
        
        if self._mode == SET:
            self._mode_str = SET_STR
        elif self._mode == EXECUTE:
            self._mode_str = EXECUTE_STR
        elif self._mode == REPORT:
            self._mode_str = ""
        
        if self.name not in (*AT_COMMANDS.keys(), *AT_COMMANDS_REPORT): # make sure command is defined
            raise CommandNotFoundError("Command not found or not defined")

        if self._mode not in (GET, SET, EXECUTE, REPORT):
            raise CommandError("Invalid command mode {mode} - must be GET, SET or EXECUTE")
        
        if self._mode == SET: # fields are present only when SET command for REPORT a special method is used
            self._set_attributes(**kwargs) # set , command fields

    def _set_attributes(self, **kwargs):
        """
        This method is used to set command fields such as port, seq, len, etc.
        """

        fields_list = AT_COMMANDS[self.name] # defualt fields defined in AT_COMMAND
        fields_passed = kwargs.keys()
        if len(kwargs) == 0: # if no kwargs, assume all fields are null (normal value)
            self._set_default_attribute()
            return
        else:
            for field in fields_list:
                if field[0] in fields_passed:
                    try:
                        setattr(self, field[0], field[1](kwargs[field[0]]))
                    except CommandError:
                        raise CommandError("Invalid field type {type}".format(type=field[1]))
                else:
                    try:
                        setattr(self, field[0], field[1]())
                    except CommandError:
                        raise CommandError("Invalid field type {type}".format(type=field[1]))

    def _set_default_attribute(self):
        
        fields_list = AT_COMMANDS_REPORT[self.name] if self._mode == REPORT else AT_COMMANDS[self.name]
        for field in fields_list:
            try:
                setattr(self, field[0], field[1]())
            except CommandError:
                raise CommandError("Invalid field type {type}".format(type=field[1]))
    
    def serilize(self):
        """
        This method is used to serilize(convert to string) AT command to send to the gateway.
        """
        # construct the payload first
        self._payload = "" if self._mode != REPORT else "" # intialize payload
        if self._mode == REPORT: # TOCHECK doesn't make sense
            return "^" + self.name + "=" + self._payload 
        if self._mode == GET:
            self._payload = ""
        elif self._mode == SET:
            fields_list = AT_COMMANDS[self.name]
            for field in fields_list:
                self._payload += "<" if field[0] == "data" else ""
                self._payload += str(getattr(self, field[0])) + ","
            self._payload = self._payload[:-1] # remove last comma
        elif self._mode == EXECUTE:
            self._payload = ""
        
        cmd_str = AT_CMD_PREFIX + self.name + self._mode_str + self._payload + CRLF
        return cmd_str
    
    def decode_data(self):
        """
        This method decodes the received data based on the message codec file.
        
        NOTE: Needs to add error handling
        """

        if self._mode == 3:
            if type(self.data) == str:
                message = Message(self.data, self.port)
                return message.decode_message()

    @staticmethod 
    def construct_from_payload(command_name, mode, payload):
        """
        This method is used to for parsing the recived data.

        :param command_name: name of the command
        :param type: command type (REPORT or others)
        :param payload: data recived from the device
        """

        command = Command(command_name, mode=mode)
        command._payload = payload

        fields_list = AT_COMMANDS_REPORT[command_name] if mode == REPORT else AT_COMMANDS[command_name] 
        for idx, field in enumerate(fields_list):
            if field[0] == "data": # TOCHECK 
                payload[idx] = payload[idx].replace("<", "")
            command.__setattr__(field[0], field[1](payload[idx]))
        return command               

    @staticmethod
    def command_check(command_str):
        """
        Check if data contains AT Commands, if found return (command_name, payload).
        
        .. NOTE::
            Make sure command_str is already decoded and doesn't have \r\n

        :returns:
            :command_name: name of the command
            :command_mode: mode of the command (REPORT or others)
            :payload: command payload
        """
        match = re.match(COMMAND_REGEX, command_str)
        if match is None:
            return None, None, None
        command_name = match.groups()[0]
        command_mode = REPORT if command_str.startswith("^") else GET # we only care about REPORT here
        payload_index = match.regs[0][1]
        payload = command_str[payload_index:].split(",")
        return command_name, command_mode, payload
#---------from commands2.py-------------end---------


"""
Start from here 
    
"""
user_name = str(input("Hello. Please enter your name: "))
print("---Welcome To LoRa Checker, " + user_name + "---")
# print("---Welcome To LoRa Checker, " + input("Hello. Please enter your name: ") + "---")

# =============================================================================
# while start = input("Ready to fetch LoRa data?.. (y/n)")
# if start == "y" :
#     print("Fetching data...")
#     lora.lora = SerialCommunication ("/dev/ttyUSB0", 9600, timeout=1)
#     lora.connect()
# elif start == "no" :
#     print("Process cancelled.")
# else:
#     print("Please enter 'y' for yes or 'n' for no.")
#     return start
# =============================================================================

"""
Done: Display which port the module is connected and status connection 
    
"""
# lora = SerialCommunication ("/dev/ttyUSB0", 9600, timeout=1) 
# lora = Lora("/dev/ttyUSB0", 9600, timeout=0.1)
# lora.connect() #display status port connection whether successful or not 
"""
TO DO: OPTIONAL*
    Port checker to check which port the module is connected to
    add print "Ready to fetch module data?" or 
    print "Ready to fetch module data. . ." 
"""

"""
TO DO: 
    Display current data in module (try 1 data first).
    Must serilize AT+Command before sent to module for cleaner output. 
"""
# command_raw = "^LRRECV:1,22,-44,29,2,<ABCD,923.2,2\r\n".strip()
# command_raw = '^LRRECV:47,31,-72,8,20,<120F2874885861F101417325400FA0F0FA0F30FF,923.2,2\r\n'.strip()
# command_raw = "^LRJOIN:481.5,0"
# command_raw = "^LRCONFIRM:1,-128,10,481.5,0"
# name, mode, payload = Command.command_check(command_raw)
# print(name, mode, payload)
# lrrecv = Command.construct_from_payload(name, mode, payload)

# time.sleep(0.1)
# print("coming data: ",  lora.is_available)
# data = lora.readlines()
# print(data)

# status = Command("STATUS", GET)
# print(status.serilize())
# time.sleep(0.1)
# lora.send_raw_command(status)

# print(lrsend.serilize())

# device_class = Command("DEVCLASS", SET)
# device_class = Command("DEVCLASS", GET)
# print(device_class.serilize())

"""
TO DO: 
    Need to check first, then options whether to change or keep DEVCLASS
"""



# from serial_communication2 import *
# import io

# lora = SerialCommunication ("/dev/ttyUSB0", 9600, timeout=1)
# lora.connect()
# lora.send(b"AT+DEVINFO=?\r\n")
# time.sleep(0.1)
# print("coming data: ",  lora.is_available)
# data = lora.readlines()
# print(data)



# if dev_info.info == :
#     print("Data checked is OK")

# ser = serial.Serial()
# ser.baudrate = 9600
# ser.port = '/dev/ttyUSB0'

# ser.open()
# print(ser.is_open)

# sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

# sio.write() 
# sio.flush()
# response = sio.readline()
# print(response)
# from serial_communication import *
# from commands import *
# from m300h import *

# if self._connected == True:
#     print("INFO: Connected Successfully to port: {}".format(self._port))
    
# else:
#     print(f"Error connecting to serial port {err}")