# -*- coding: utf-8 -*-
"""
julaboController.py
Author: Andrew Hall
Version: 3.0
Updated: July 2020

Script for remote control of Julabo heater/chiller circulator and flow
direction valves.

See https://www.julabo.com/sites/default/files/he-se_protocol_0.pdf for full 
list of available commands for Julabo.

Delay for switching direction can be sent to arduino as interger values in 
seconds. Sending the command 'STATUS' returns the current status (ON, OFF, 
HOLD, ERROR). The command 'POS' returns the postion of the valves (1= ON, 
0= OFF). The valve position can be set manually using the commands 
'SET_VALVE_ON' and 'SET_VALVE_OFF'. The module is activated and deactivated 
using the commands 'SWITCH_ON' and 'SWITCH_OFF'

"""
import serial, time, sys
import serial.tools.list_ports as list_ports



class dyneo(object):
    def __init__(self, GUI=False):
        for device in list_ports.comports():
            if device.serial_number == '955303437343511161F1':
            #if device.description == 'CORIO':
                port = device.device
        try:
            self.dyneo = serial.Serial(port=port, baudrate=4800, bytesize=7, parity=serial.PARITY_EVEN, stopbits=1, timeout=0.1)
        except:
            sys.exit(1)
    
    
    def send(self, command):
        self.dyneo.reset_input_buffer()
        command = str(command) + "\r"
        self.dyneo.write(bytes(command.encode('utf-8')))
        time.sleep(0.1) # 100 ms delay to allow Julabo time to respond
        reply = self.dyneo.readline()
        if len(reply) > 0:
            reply = reply.decode('utf-8').strip('\n')
        else:
            reply = None
        return reply
        
    
    def switchOn(self):
        self.send('out_mode_05 1')
        
        
    def switchOff(self):
        self.send('out_mode_05 0')


    def readTemp(self):
        try:
            temp = float(self.send('in_pv_02'))
        except:
            temp = None
        return temp
    
    
    def setTemp(self,setpoint):
        self.send('out_sp_00 ' + str(setpoint))
        print('Set temperature: ' + str(setpoint) + u'\N{DEGREE SIGN}C')
        
        
    def setTemp_wait(self, setpoint):
        self.setTemp(setpoint)
        startTime = time.time()
        
        temp = self.readTemp()
        
        n = 0
        while n < 60:
            temp = self.readTemp()
            print('\rActual temperature: ' + str(temp) + u'\N{DEGREE SIGN}C', end=' ')
            if temp > setpoint-0.1 and temp < setpoint+0.1:
                n += 1
            else:
                n = 0
            time.sleep(1)
    
        elapsedTime = round(time.time() - startTime)
        print('\nSetpoint reached. Elapsed time: ' + str(elapsedTime))


    def checkStatus(self):
        status = self.send('status')
        return status
    
    
    def close(self):
        self.dyneo.close()
        sys.exit()





class valves(object):
    def __init__(self):
        for device in list_ports.comports():
            if device.serial_number == '55736323239351918101':
                port = device.device
        try:
            self.valves = serial.Serial(port=port, baudrate=9600, timeout=0.1)
            time.sleep(2)  # Arduino takes a couple of seconds to wake up
        except:
            raise AttributeError
    
    
    def send(self, command):
        self.valves.reset_input_buffer()
        command = str(command) + "\n"
        self.valves.write(bytes(command.encode('utf-8')))
        reply = self.valves.readline()
        return reply.decode('utf-8')
    
    
    def switchOn(self):
        self.send('SWITCH_ON')
        
        
    def switchOff(self):
        self.send('SWITCH_OFF')
        
        
    def checkStatus(self):
        status = self.send('STATUS')
        return status


    def readPosition(self):
        position = self.send('POS')
        return position
    
    
    def setPosition(self, position):
        if position == 0:
            self.send('SET_VALVE_OFF')
        else:
            self.send('SET_VALVE_ON')
        
        
    def setDelay(self,delay):
        if delay > 0:
            self.send(delay)
        
        
    def close(self):
        self.valves.close()
        sys.exit()


