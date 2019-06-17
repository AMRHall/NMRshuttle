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

class fieldMap(object):

    def __init__(self,motorPort='/dev/ttyACM0',sensorPort='/dev/ttyACM1'):
        # Open communications with motor driver
        PyTrinamic.showInfo()
        PyTrinamic.showAvailableComPorts()
        
        myInterface = serial_tmcl_interface(motorPort)
        self.module = TMCM_1160(myInterface)
        print("\n")
        
        self.module.setActualPosition(0)
        
        # Open communications with sensor Arduino board
        self.sens = sensorShield.sensorShield(port=sensorPort)
        self.sens.openSensors()
      
        
        
    def recordFieldMap(self):
        # Get some parameters from the motor
        pulseDiv = self.module.axisParameter(154)
        uStepRes = self.module.axisParameter(140)
        fullStepRot = 200
        NStep = fullStepRot*uStepRes
        
        # Set speed for motor
        Circ = float(input("Motor wheel diameter (cm): "))
        speed = float(input("Target motor speed (cm/s): "))
        speedPPS = int(((speed/Circ) * fullStepRot * (2**uStepRes) * (2**pulseDiv) * 2048 * 32)/(16 * (10**6)))
        self.module.setTargetSpeed(speedPPS)
        
        # Get parameters
        points = int(input("Number of points to use in generating field map: "))
        maxHeight = float(input("Maximum height to measure: "))
        spacing = input("Use logarithmic (log) or linear (lin) spacing? ")
        
    
        # Calculate number of steps
        if spacing == 'lin' or 'LIN':
            distance = np.linspace(0,maxHeight,points,dtype=float)
        elif spacing == 'log' or 'LOG':
            distance = np.geomspace(1,maxHeight,points,dtype=float)
            
        fieldStrength=[]
        
        for x in distance:
            steps = int((x*NStep)/Circ)
            field = self.recordField(steps)
            fieldStrength.append(field)
            print('Distance: ' + str(x) + 'cm, Field strength: ' + str(field) + 'mt')
        
        # Plot and fit the results
        self.plot()
        print('\n')
        
        # Print data
        data = list(zip(distance,fieldStrength))
        print(data)
        print('\n')
        
        # Save data
        saveData = input("Save data (Y/N)? ")
        if saveData == 'y' or 'Y':
            np.save('fieldMap.csv',data)
        
            
    def recordField(self,steps):
        # Move motor to position
        self.module.moveToPosition(steps)
        
        time.sleep(1)
        
        # Save field strength reading from 2Dex sensor
        self.sens.clearBuffer()
        self.sens.readSensors()
        field = self.sens.hallSens
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
        plt.plot(np.linspace(0, 100, 101, dtype=float), fit(np.linspace(0, 100, 101, dtype=float), params[0], params[1],params[2]),label='Fitted function')
        plt.show()
        
        print('B(z) = B(0)/(1-(z/a)^b)')
        print('Fitting parameters: B0=' + str(round(params[2],3)) + ', a=' + str(round(params[0],3)) + ', b=' + str(round(params[1],3)))
        
