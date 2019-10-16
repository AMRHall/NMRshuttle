#
# fieldMap.py
# Version 1.0, Jun 2019
#
# Andrew Hall 2019 (c)
# a.m.r.hall@soton.ac.uk
#
# Python script for automated measuring pf field strength vs. distance
# Uses 2Dex hall sensor and Trinamic TMCM-1060 or TMCM-1160 motor.
# Requires Python 3.6 or later.
#
#

import sensorShield
import PyTrinamic
from PyTrinamic.connections.serial_tmcl_interface import serial_tmcl_interface
from PyTrinamic.modules.TMCM_1160 import TMCM_1160
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
import sys, os

class fieldMap(object):

    def __init__(self):
         # Open communications with sensor Arduino board and motor
        for device in list_ports.comports():
            if device.serial_number == '55739323637351819251':
                sensorPort = device.device
            elif device.description == 'Trinamic Stepper Device':
                motorPort = device.device
        try:
            self.sens = sensorShield.sensorShield(port=sensorPort, timeout=0.1)
        except:
            print('Sensor device not found')
            sys.exit()
        try:
            myInterface = serial_tmcl_interface(motorPort)
            self.module = TMCM_1160(myInterface)
        except:
            print('Motor device not found')
            sys.exit()
            
        print("Opened connection to sensors")
        PyTrinamic.showInfo()
        PyTrinamic.showAvailableComPorts()

        print("\n")
        
       
        
      
        
        
    def recordFieldMap(self, motor='TMCM-1160'):
        # Get some parameters from the motor
        pulseDiv = self.module.axisParameter(154)
        uStepRes = self.module.axisParameter(140)
        fullStepRot = 200
        NStep = fullStepRot*2**uStepRes
        
        # Set speed for motor
        Circ = float(input("Motor wheel diameter (cm): "))
        speed = float(input("Target motor speed (cm/s): "))
        if motor == 'TMCM-1160':
            speedPPS = int(((speed/Circ) * fullStepRot * (2**uStepRes) * (2**pulseDiv) * 2048 * 32)/(16 * (10**6)))
        elif motor == 'TMCM-1060':
            speedPPS = int((speed/Circ) * fullStepRot * (2**uStepRes))
        else:
            print("Motor type not recognised")
            return
        self.module.setTargetSpeed(speedPPS)
        
        # Get parameters
        points = int(input("Number of points to use in generating field map: "))
        self.maxHeight = float(input("Maximum height to measure: "))
        spacing = input("Use logarithmic (log) or linear (lin) spacing? ")
        
    
        # Calculate number of steps
        if spacing == 'lin' or 'LIN':
            self.distance = np.linspace(0,self.maxHeight,points,dtype=float)
        elif spacing == 'log' or 'LOG':
            self.distance = np.geomspace(1,self.maxHeight,points,dtype=float)
        else:
            print("Spacing must be either 'LOG' or 'LIN'")
            return
        print("\n")    
        self.fieldStrength=[]

        # Set motor to home position
        self.module.moveToPosition(0)
        time.sleep(5)
        
        # record field strength at different distances
        for x in self.distance:
            steps = int((x*NStep)/Circ)
            field = self.recordField(steps)
            self.fieldStrength.append(field)
            print('Distance: ' + str(round(x,1)) + 'cm, Field strength: ' + str(field) + 'mT')
        print("\n")   

        # Plot and fit the results
        self.plot()
        print('\n')
        
        # Print data
        data = list(zip(self.distance,self.fieldStrength))
        print(data)
        print('\n')
        
        # Save data
        saveData = input("Save data (Y/N)? ")
        if saveData == 'y' or 'Y':
            np.savetxt('fieldMap.csv',data,delimiter=',',newline='\n',header="Position (cm), Field Strength (mT)")
        
            
    def recordField(self,steps):
        # Move motor to position
        self.module.moveToPosition(steps)
        
        time.sleep(1)
        
        # Suppress printing output from sensorShield
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

        # Save field strength reading from 2Dex sensor
        self.sens.clearBuffer()
        while True:
            line = self.sens.readSensors()
            if line != None and len(line) > 25:
                field = self.sens.hallSens
                break

        # Reable printing
        sys.stdout.close()
        sys.stdout = original_stdout
        return field
        
    
        
    def plot(self):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        
        ax.plot(self.distance, self.fieldStrength, 'x')
        
        plt.title('Field strength vs. Distance')
        ax.set_ylabel('Field strength (mT)')
        ax.set_xlabel('Distance from centre of magnet (cm)')
        
        
        # Fit data
        fit = lambda x,a,b,c: c/(1+((x/a)**b))
        params, params_covariance = optimize.curve_fit(fit, self.distance, self.fieldStrength, p0=[20,5,7000])
        plt.plot(np.linspace(0, self.maxHeight, 101, dtype=float), fit(np.linspace(0, self.maxHeight, 101, dtype=float), params[0], params[1],params[2]),label='Fitted function')
        plt.show()
        
        print('B(z) = B(0)/(1-(z/a)^b)')
        print('Fitting parameters: B0=' + str(round(params[2],3)) + ', a=' + str(round(params[0],3)) + ', b=' + str(round(params[1],3)))
        
