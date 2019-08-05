# -*- coding: utf-8 -*-
"""
julaboController.py

Author: Andrew Hall
Version: 1.0
Updated: 5th Aug 2019

Script for remote control of Julabo heater/chiller circulator
See https://www.julabo.com/sites/default/files/he-se_protocol_0.pdf for full 
list of available commands.

"""

import serial
import time

class dyneo(object):
    def __init__(self,port='COM4'):
        self.dyneo = serial.Serial(port=port, baudrate=4800, bytesize=7, parity=serial.PARITY_EVEN, stopbits=1, timeout=0.1)
    
    
    def switchOn(self):
        self.dyneo.write(b'out_mode_05 1\r')
        
        
    def switchOff(self):
        self.dyneo.write(b'out_mode_05 0\r')


    def readTemp(self):
        self.dyneo.write(b'in_pv_02\r')
        reply = str(self.dyneo.readline())
        temp = float(reply.strip("b'\\r\\n"))
        return temp
    
    
    def setTemp(self,setpoint):
        templist = []
        avgtemp = 0
        
        self.dyneo.write(bytes('out_sp_00 ' + str(setpoint) + '\r', 'utf-8'))
        
        print('Set temperature: ' + str(setpoint) + u'\N{DEGREE SIGN}C')

        while avgtemp < setpoint-0.1 or avgtemp > setpoint+0.1:
            temp = self.readTemp()
            templist.append(temp)
            templist = templist[-25:]
            avgtemp = sum(templist)/len(templist)
            print('\rActual temperature: ' + str(temp) + u'\N{DEGREE SIGN}C', end = ' ')
            time.sleep(1)
    
        print('\nSetpoint reached')


    def checkStatus(self):
        self.dyneo.write(b'status\r')
        status = str(self.dyneo.readline()).strip("b'\\r\\n")
        return status
    
    def close(self):
        self.dyneo.close()
