 # Import libraries and define functions
import PyTrinamic
from PyTrinamic.connections.serial_tmcl_interface import serial_tmcl_interface
from PyTrinamic.modules.TMCM_1160 import TMCM_1160
import time
import datetime 

# Import default values from setup file
setup = open("NMRshuttle_setup.txt","r").read()

# Define parameters of magnet + shuttle system
MaxHeight = float((setup.split('MaxHeight: ')[1].split('\n')[0]))        # Maximum height of sample (cm)
B0 = float((setup.split('B0: ')[1].split('\n')[0]))                # Magnetic field strength at centre of magnet (Tesla)
a = float((setup.split('a: ')[1].split('\n')[0]))                   # Magnetic field fitting parameter 1 
b = float((setup.split('b: ')[1].split('\n')[0]))                     # Magnetic filed fitting parameter 2
Circ = float((setup.split('Circ: ')[1].split('\n')[0]))		         # Circumference of spindle wheel (cm)
NStep = int((setup.split('NStep: ')[1].split('\n')[0]))       # Number of steps for one full revolution of motor
speed = int((setup.split('speed: ')[1].split('\n')[0]))         # Target motor speed
acceleration = int((setup.split('accel: ')[1].split('\n')[0]))        # Motor acceleration


PyTrinamic.showInfo()
PyTrinamic.showAvailableComPorts()

# For usb connection
port = (setup.split('serial: ')[1].split('\n')[0])
myInterface = serial_tmcl_interface(port)

module = TMCM_1160(myInterface)

# Motor settings
module.setTargetSpeed(speed)
module.setAcceleration(acceleration)



# Open file with list of magnetic field strength
VBlist = open("VBlist.txt","r").read().splitlines()

# Get number of transients for each field strength
NS = int(input("Number of transients at each magnetic field strength: "))

for x in VBlist:
  # Check for error flags
  if errflag != 0:
       break
    
	# Fetch desired magnetic field strength (mT)
  BSample = float(x)
  print("\nMagnetic field strength =", BSample, "mT")
    
  # Calculate sample position needed to achieve this field strength
  dist = float(b*(((B0/BSample)-1)**(1/a)))
  print("Height = ", dist, " cm")
    
  # Error if sample position too high or too low
  if (dist < 0)  or (dist > MaxHeight):
       print('Field strength out of range!')
       errflag += 1
       break
    
  # Calculate number of steps
  steps = int((dist*NStep)/Circ)
  print("Number of steps =", steps, '\n')
  
  module.setUserVariable(9,steps)
  
  
