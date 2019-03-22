
#
# NMRshuttle.py
# Version 2.0, Mar 2019
#
# Andrew Hall 2019 (c)
# a.m.r.hall@soton.ac.uk
#
# Python script for controlling NMR low field shuttle with Trinamic TMCM-1060 or TMCM-1160 motor using TopSpin.
# Includes options for different NMR tubes and for arbitarily defined velocity/distance profiles.
# Requires setup file containing motor parameters. Also requires PyTrinamic and Serial libraries.
# 
#


# Import libraries and define functions
import NMRShuttleSetup
import sys
import PyTrinamic
from PyTrinamic.connections.serial_tmcl_interface import serial_tmcl_interface
from PyTrinamic.modules.TMCM_1160 import TMCM_1160
import time
import datetime 

# Import default values from setup file
setup = NMRShuttleSetup.NMRShuttle()

# Define parameters of magnet + shuttle system
MaxHeight = setup.maxHeight        # Maximum height of sample (cm)
B0 = setup.B0              # Magnetic field strength at centre of magnet (Tesla)
a = setup.a                 # Magnetic field fitting parameter 1 
b = setup.b                     # Magnetic filed fitting parameter 2
Circ = setup.circ		         # Circumference of spindle wheel (cm)
NStep = setup.NStep       # Number of steps for one full revolution of motor
speed = int(sys.argv[1])				         # Target motor speed
ramp = setup.ramp         # Equation for velocity ramp

PyTrinamic.showInfo()
PyTrinamic.showAvailableComPorts()

# For usb connection
myInterface = serial_tmcl_interface(setup.port)

module = TMCM_1160(myInterface)

# Get operation mode
mode = int(sys.argv[2]) # 1 = Constant velocity, 2 = Velocity sweep
if mode != (1 or 2):
  ERRMSG("Invalid value for operation mode.", modal=1)
  EXIT()

# Get tube type
type = int(sys.argv[3]) # 1 = Standard glass tube, 2 = 5mm High pressure tube, 3 = 10mm High pressure tube
if type == 1:
  stallGuard = NMRShuttleSetup.stallGuard_stan()
elif type == 2:
  stallGuard = NMRShuttleSetup.stallGuard_HP5()
elif type == 3:
  stallGuard = NMRShuttleSetup.stallGuard_HP10()
else:
  ERRMSG("Invalid value for tube type.", modal=1)
  EXIT()

# Motor settings
module.setMaxVelocity(setup.maxSpeed)
module.setMaxAcceleration(setup.accel)

module.motorRunCurrent(stallGuard.motorRunCurrent)
module.motorStandbyCurrent(stallGuard.motorStandbyCurrent)
module.stallguard2Filter(stallGuard.stallguard2Filter)
module.stallguard2Threshold(stallGuard.stallguard2Threshold)
module.stopOnStall(stallGuard.stopOnStall)

if mode == 1:
  module.setTargetSpeed(speed)

# Reset all error flags
errflag = 0
module.setUserVariable(9,0)

# Get number of transients for each field strength
NS = int(sys.argv[5])

# Fetch desired magnetic field strength (mT)
BSample = float(sys.argv[4])
status_msg = str("\nMagnetic field strength =", BSample, "mT")
SHOW_STATUS(status_msg)
    
# Calculate sample position needed to achieve this field strength
dist = float(b*(((B0/BSample)-1)**(1/a)))
status_msg = str("Height = ", dist, " cm")
SHOW_STATUS(status_msg)
    
# Error if sample position too high or too low
if (dist < 0)  or (dist > MaxHeight):
	ERRMSG("Field strength out of range!", modal=1)
	errflag += 1
    
# Calculate number of steps
steps = int((dist*NStep)/Circ)
status_msg = str("Number of steps =", steps)
print(status_msg)

module.setUserVariable(1,steps)
  
# Check position of sample and wait until finished
n = 0
up = 'n'
start_position = module.actualPosition()
while n < NS:	
	# Check for errors in motor
	error = module.userVariable(9)
	if error == 1:		#Shutdown error from light gate
		ERRMSG("Emergency stop detected. Aborting acquisition.", modal=1)
		errflag += 1
		break
	elif error == 2:       #Stall detected
		ERRMSG("Stall detected. Aborting acquisition.", modal=1)
		errflag += 1
		break
	
	#Check sample position
	position = module.userVariable(8)
	if up == 'n' and position == 1:
		up = 'y'
		status_msg = str("Sample up in ", elapsed_time, " seconds.")
		SHOW_STATUS(status_msg)
	if up == 'y' and position == 0:
		up = 'n'
		n += 1
		status_msg = str("Sample down in ", elapsed_time, " seconds.")
		SHOW_STATUS(status_msg)
		status_msg = str("Completed transient", n, "of", NS, "at magnetic field strength of", BSample, "mT")
		SHOW_STATUS(status_msg)
	if position == 2 and mode == 2:
		curr_position = ((module.actualPosition()-start_position)*-Circ)/NStep
		speed = int(eval(ramp))
		module.setTargetSpeed(speed)
		
# Once sequence is complete for all magnetic field strengths:
# Set motor distance back to zero for safety
module.setUserVariable(1,0)

# Print competion message
timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
if errflag ==0:
	status_msg = str("\nSequence successfully completed at", timestamp)
	ERRMSG(status_msg)
else:
	status_msg = str("\nSequence aborted with", errflag, "error(s) at", timestamp)
	ERRMSG(status_msg, modal=1)

# Close serial port
myInterface.close()
