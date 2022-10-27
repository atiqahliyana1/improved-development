#!/usr/bin/env python3
"""
@author: Ali Mahmoud Mohammed Madani
@email: codeparamedic@gmail.com
"""

"""
Module To-do:
[X] Create basic decoder for GIS data (bare bones)
[] Create class-based message handler (OOP) for:
    [X] Decoding
    [] Encoding
[] Add validation and error handling
"""

"""
Input to Message:
 - Payload (ex. <128F2876371857F101416567900FA0F1F97837614000F30F)
 - Port (ex. 31)

Functions of Message:
 - Encode outgoing message
 - Decode incoming message

Output of Message:
 - Encoded/Decoded message
"""

"""
STAGE 1
"""

# def decode(message, port):
#     field_names = ['id', 'latitude', 'longitude', 'altitude', 'initial', 'bearing', 'task_id']
#     data_class = _port_definition(port)
#     if data_class == None:
#         return "INCORRECT PORT"
    
#     message = message[1:] # remove '<'
#     if data_class == 'GIS_data':
#         data_list = message.split('F')
#         data_dict = {}
#         for x in range(len(field_names)):
#             data_dict[field_names[x]] = _dot(_A0(data_list[x]))
#         return data_dict
#     else:
#         return "TBC"
        
# def _port_definition(port):
#     if port == 31:
#         return 'GIS_data'
#     elif port == 30:
#         return 'GIS_control'
#     else:
#         return None

# def _A0(data):
#     if data != "A0":
#         return data
#     return '0000000000'

# def _dot(data):
#     l = len(data)
#     if l < 10:
#         return data
#     return data[:l-9] + '.' + data[l-9:]

"""
STAGE 2
"""

from message_codec import *

class Message:

    def __init__(self, message, port):
        self.message = message
        self.port = port
        self._port_definition = PortDefinition(port)
        self._port_codec = port_codec[self._port_definition]
        self._decimal_precision = decimal_precision[self._port_definition]
    
    def decode_message(self):
        """
        This method decodes downlinked data and returns them in a dictionary
        """
        decoded_dict = {}
        # self._switch_angle_bracket()
        message_components = [component for component in self.message.split(SPLITTER) if component]
        for (i, var_codec) in enumerate(self._port_codec):
            if var_codec[1] == TrueType.DECIMAL:
                decoded_dict[var_codec[0]] = self._switch_decimal_point(
                    self._switch_zero_filler(message_components[i])
                )
            else:
                decoded_dict[var_codec[0]] = message_components[i]
        return decoded_dict
    
    def _switch_zero_filler(self, zero):
        if zero == ZERO_FILLER:
            return ZERO_FULL
        if zero == ZERO_FULL:
            return ZERO_FILLER
        return zero
    
    def _switch_decimal_point(self, number):
        p = self._decimal_precision
        l = len(number)
        if DOT in number:
            return number[:l-p] + number[l-p-1:]
        return number[:l-p] + DOT + number[l-p:]
    
    def _switch_angle_bracket(self):
        """
        REDUNDANT - Already existing in Commands module
        """
        if ANGLE_BRACKET in self.message:
            self.message = self.message[1:]
        else:
            self.message = ANGLE_BRACKET + self.message

"""
TESTING
"""


# print(decode("<128F2876371857F101416567900FA0F1F97837614000F30F", 31))
# print(decode("<129F2876361877F101416640400FA0F0FA0F30FF", 31))

# mes = Message("<128F2876371857F101416567900FA0F1F97837614000F30F", 31)
# print(mes.decode_message())