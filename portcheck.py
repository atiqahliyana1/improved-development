#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 14:58:52 2022

@author: meraque
"""
# from serial import Serial, SerialException, SerialTimeoutException
import time
import serial
import serial.tools.list_ports
import sys
import glob

def portcheck(): 
    
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
        print("Successfully connected to port {}".format(ports))
        
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
        print("Successfully connected to port {}".format(ports))
        
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

if __name__ == '__main__' :
    print(portcheck())