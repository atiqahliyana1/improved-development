#!/usr/bin/env python3
from enum import IntEnum, unique, auto

SPLITTER = 'F'
ZERO_FILLER = 'A0'
ZERO_FULL = '0000000000' # Should switch with one 0 and multiply with precision codec
DOT = '.'
ANGLE_BRACKET = '<'

@unique
class TrueType(IntEnum):
    INTEGER = auto()
    DECIMAL = auto()
    BOOLEAN = auto()

@unique
class PortDefinition(IntEnum):
    GIS_CONTROL = 30
    GIS_DATA = 31

port_codec = {
    PortDefinition.GIS_DATA: (
        ('cloud_id', TrueType.INTEGER),
        ('latitude', TrueType.DECIMAL),
        ('longitude', TrueType.DECIMAL),
        ('altitude', TrueType.DECIMAL),
        ('initial', TrueType.BOOLEAN),
        ('bearing', TrueType.DECIMAL),
        ('task_id', TrueType.INTEGER)
    )
}

"""
For future data other than GIS, a different decimal point precision might
be needed (ex. 4, not only 9). So a dictionary is made for the precision
"""

decimal_precision = {
    PortDefinition.GIS_DATA: 9
}

# for port in TrueType:
#     print(port)
#     print(repr(port))
#     print(type(port))
#     print(port.name)
#     print(port.value)
# print(port_codec[PortDefinition.GIS_DATA])