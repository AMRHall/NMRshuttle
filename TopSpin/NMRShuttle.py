
#
# NMRshuttle.py
# Version 2.1, Mar 2019
#
# Andrew Hall 2019 (c)
# a.m.r.hall@soton.ac.uk
#
# Python script for controlling NMR low field shuttle with Trinamic TMCM-1060 or TMCM-1160 motor using TopSpin.
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

# Print information about script
print("\n\nNMRshuttle_VBlist\nVersion 5\nThis program is for controlling a NMR low field shuttle using a TMCM-1060 or TMCM-1160 motor.\nCopyright (c) Andrew Hall, 2019\nFor further details see https://github.com/AMRHall/NMR_Shuttle/blob/master/README.md\n\n\n")

# Import default values from setup file
setup = NMRShuttleSetup.NMRShuttle()

# Define parameters of magnet + shuttle system
MaxHeight = setup.maxHeight        # Maximum height of sample (cm)
B0 = setup.B0              # Magnetic field strength at centre of magnet (Tesla)
a = setup.a                 # Magnetic field fitting parameter 1 
b = setup.b                     # Magnetic filed fitting parameter 2
Circ = setup.circ		         # Circumference of spindle wheel (cm)
NStep = setup.NStep       # Number of steps for one full revolution of motor
speed = setup.speed				         # Target motor speed
ramp = setup.ramp         # Equation for velocity ramp

# Get operation mode
mode = int(sys.argv[1]) # 1 = Constant velocity, 2 = Velocity sweep
if mode != (1 or 2):
  print("Invalid value for operation mode.")
  sys.exit(0)

# Get tube type
type = int(sys.argv[2]) # 1 = Standard glass tube, 2 = 5mm High pressure tube, 3 = 10mm High pressure tube
if type == 1:
  stallGuard = NMRShuttleSetup.stallGuard_stan()
elif type == 2:
  stallGuard = NMRShuttleSetup.stallGuard_HP5()
elif type == 3:
  stallGuard = NMRShuttleSetup.stallGuard_HP10()
else:
  print("Invalid value for tube type.")
  sys.exit(0)

PyTrinamic.showInfo()
PyTrinamic.showAvailableComPorts()

# For usb connection
myInterface = serial_tmcl_interface(setup.serial)

module = TMCM_1160(myInterface)

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
NS = int(sys.argv[4])

# Get number of 2D slices
TD = int(sys.argv[5])

# Fetch desired magnetic field strength (mT)
BSample = int(sys.argv[3])
print(str("\nMagnetic field strength = " + str(BSample) +  " mT"))

    
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
print(str("Number of steps = " + str(steps)))

module.setUserVariable(1,steps)
  
# Check position of sample and wait until finished
up = 'n'
start_position = module.actualPosition()
m = 0
while m < TD:
	n = 0
	while n < NS:	
		# Check for errors in motor
		error = module.userVariable(9)
		if error == 1:		#Shutdown error from light gate
			print("\nEmergency stop detected. Aborting acquisition.")
			errflag += 1
			break
		elif error == 2:       #Stall detected
			print("\nStall detected. Aborting acquisition.")
			errflag += 1
			break
	
		#Check sample position
		position = module.userVariable(8)
		if up == 'n' and position == 1:
			up = 'y'
			print("Sample up.")
		if up == 'y' and position == 0:
			up = 'n'
			n += 1
			print("Sample down.")
			if TD == 1:
				print(str("Completed scan " + str(n) + " of " + str(NS) + " at magnetic field strength of " + str(BSample) + " mT\n"))
			else:
				print(str("Completed scan " + str(n) + "/" + str(NS) + " for 2D slice" + str(m) + "/" + str(TD) + " at magnetic field strength of " + str(BSample) + " mT\n"))
		if position == 2 and mode == 2:
			curr_position = ((module.actualPosition()-start_position)*-Circ)/NStep
			speed = int(eval(ramp))
			module.setTargetSpeed(speed)
	td += 1
		
# Once sequence is complete for all magnetic field strengths:
# Set motor distance back to zero for safety
module.setUserVariable(1,0)

# Print competion message
timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
if errflag ==0:
	print(str("\nSequence successfully completed at " + str(timestamp)))
else:
	print(str("Sequence aborted with " + str(errflag) + " error(s) at " + str(timestamp) + "\n"))

# Close serial port
myInterface.close()
