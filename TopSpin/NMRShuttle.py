#
# NMRshuttle.py
# Version 2.2, Apr 2019
#
# Andrew Hall 2019 (c)
# a.m.r.hall@soton.ac.uk
#
# Python script for controlling NMR low field shuttle with Trinamic TMCM-1060 or TMCM-1160 motor.
# Includes options for different NMR tubes and for arbitarily defined velocity/distance profiles.
# Requires setup file containing motor parameters. Also requires PyTrinamic and Serial libraries.
# Requires Python 3.6 or later.
#


# Import libraries and define functions
import NMRShuttleSetup
import sys
import PyTrinamic
from PyTrinamic.connections.serial_tmcl_interface import serial_tmcl_interface
from PyTrinamic.modules.TMCM_1160 import TMCM_1160
import time
import datetime
import math

# Print information about script
print("NMRshuttle.py\nVersion 2.2\nThis program is for controlling a NMR low field shuttle using a TMCM-1060 or TMCM-1160 motor.\nCopyright (c) Andrew Hall, 2019\nFor further details see https://github.com/AMRHall/NMR_Shuttle/blob/master/README.md\n\n\n")

# Import default values from setup file
setup = NMRShuttleSetup.NMRShuttle()

# Define parameters of magnet + shuttle system
MaxHeight = setup.maxHeight        # Maximum height of sample (cm)
B0 = setup.B0                      # Magnetic field strength at centre of magnet (Tesla)
a = setup.a                        # Magnetic field fitting parameter 1 
b = setup.b                        # Magnetic filed fitting parameter 2
Circ = setup.circ		   # Circumference of spindle wheel (cm)
NStep = setup.NStep                # Number of steps for one full revolution of motor
speed = float(sys.argv[6])	   # Motor speed
accel = float(sys.argv[7])	   # Acceleration
ramp = str(sys.argv[8])            # Equation for velocity ramp


# Open communications with motor driver
PyTrinamic.showInfo()
PyTrinamic.showAvailableComPorts()

myInterface = serial_tmcl_interface(setup.serial)
module = TMCM_1160(myInterface)
print("\n")

# Reset all error flags
errflag = 0
module.setUserVariable(9,0)


# Get operation mode
mode = int(sys.argv[1]) # 1 = Constant velocity, 2 = Velocity sweep, 3 = Constant time

# Get tube type and fetch appropriate stall guard settings
tubeType = int(sys.argv[2]) # 1 = Standard glass tube, 2 = 5mm High pressure tube, 3 = 10mm High pressure tube
if tubeType == 1:
  stallGuard = NMRShuttleSetup.stallGuard_stan()
elif tubeType == 2:
  stallGuard = NMRShuttleSetup.stallGuard_HP5()
elif tubeType == 3:
  stallGuard = NMRShuttleSetup.stallGuard_HP10()
else:
  print("Invalid value for tube type.")
  sys.exit(0)

	
# Convert speed and acceleration from real units to motor units
pulseDiv = module.axisParameter(154)
uStepRes = module.axisParameter(140)
fullStepRot = 200
rampDiv = module.axisParameter(153)

speed = int(((speed/Circ) * fullStepRot * (2**uStepRes) * (2**pulseDiv) * 2048 * 32)/(16 * (10**6)))
maxSpeed = int(((setup.maxSpeed/Circ) * fullStepRot * (2**uStepRes) * (2**pulseDiv) * 2048 * 32)/(16 * (10**6)))
accel = int(((accel/Circ) * fullStepRot * (2**uStepRes) * (2**(rampDiv + pulseDiv + 29)))/((16 * (10**6))**2))

# Motor settings
module.setMaxVelocity(maxSpeed)
module.setMaxAcceleration(accel)

module.motorRunCurrent(stallGuard.motorRunCurrent)
module.motorStandbyCurrent(stallGuard.motorStandbyCurrent)
module.stallguard2Filter(stallGuard.stallguard2Filter)
module.stallguard2Threshold(stallGuard.stallguard2Threshold)
module.stopOnStall(stallGuard.stopOnStall)

if mode == 1 or mode == 3:
  module.setTargetSpeed(speed)
  print("Target speed = " + str(speed))
print("Acceleration = " + str(accel))


# Fetch desired magnetic field strength (mT)
BSample = float(sys.argv[3])
print(str("Magnetic field strength = " + str(BSample) +  " mT"))

    
# Calculate sample position needed to achieve this field strength
dist = float(b*(((B0/BSample)-1)**(1/a)))
print(str("Height = " + str(dist) + " cm"))

    
# Error if sample position too high or too low
if (dist < 0)  or (dist > MaxHeight):
	print("Field strength out of range!")
	errflag += 1
	sys.exit(0)
    
# Calculate number of steps
steps = int((dist*NStep)/Circ)
print(str("Number of steps = " + str(steps) + "\n"))

module.setUserVariable(1,steps)


# Get number of transients for each field strength
NS = int(sys.argv[4])

# Get number of 2D slices
TD = int(sys.argv[5])
  
# Check position of sample and wait until finished
up = 'n'
module.setActualPosition(0)
m = 0
while m < TD:
	n = 0
	m += 1
	while n < NS:	
		# Check for errors in motor
		if module.digitalInput(10) == 0:		#Shutdown error from light gate
			print("\nEmergency stop detected. Aborting acquisition.")
			errflag += 1
			break
		elif module.statusFlags() != 0:       #Stall detected
			print("\nStall detected. Aborting acquisition.")
			errflag += 1
			break
	
		#Check sample position
		position = module.userVariable(8)
		if up == 'n' and position == 1:
			up = 'y'
			print("\nSample up.")
			startTime = time.time()
		if up == 'y' and position == 1:
			elapsedTime = int(time.time() - startTime)
			print('\rElapsed time = ' + str(elapsedTime), end = '')
		if up == 'y' and position == 0:
			up = 'n'
			n += 1
			print("\nSample down.")
			if TD == 1:
				print(str("Completed scan " + str(n) + " of " + str(NS) + " at magnetic field strength of " + str(BSample) + " mT"))
			else:
				print(str("Completed scan " + str(n) + "/" + str(NS) + " for 2D slice " + str(m) + "/" + str(TD) + " at magnetic field strength of " + str(BSample) + " mT"))
		if position == 2 and mode == 2:
			currPosition = (module.actualPosition()*(-Circ))/NStep
			currField = float(B0/(1+((currPosition/b)**a)))
			rampSpeed = int(speed*eval(ramp))
			module.setTargetSpeed(rampSpeed)
			print('\rSpeed =' + str(rampSpeed), end = '')
		
# Once sequence is complete for all magnetic field strengths:
# Set motor distance back to zero for safety
module.setUserVariable(1,0)

# Print competion message
timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
if errflag ==0:
	print(str("\nSequence successfully completed at " + str(timestamp)))
else:
	print(str("\nSequence aborted with " + str(errflag) + " error(s) at " + str(timestamp) + "\n"))

# Close serial port
myInterface.close()
