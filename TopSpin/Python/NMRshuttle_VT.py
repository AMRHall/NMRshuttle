#
# NMRshuttle.py
# Version 3.0, Jul 2019
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
import PyTrinamic
from PyTrinamic.connections.serial_tmcl_interface import serial_tmcl_interface
from PyTrinamic.modules.TMCM_1160 import TMCM_1160
import time, datetime, math, signal, sys
import numpy as np
import sensorShield
import julaboController

'''
# Define what to do if terminate signal recieved from Topspin
def terminate(signal,frame):
	timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
	print(str("\nSequence terminated by Topspin at " + str(timestamp)))
	myInterface.close()
	sys.exit(-1)

def readSensors():
	sens.readSensors()
	hallSens = sens.hallSens
	temp = sens.PT100_1
			
	sensPos = np.interp(hallSens,distanceValues,fieldValues)
	calcPos = sensPos - setup.offsetDist
	calcField = np.interp(calcPos,fieldValues[::-1],distanceValues[::-1])
	return temp, calcField
				      
# Open sensors
try:
	sens = sensorShield.sensorShield()
except:
	print('sensorShield.py not installed')
calcField = 'XXX'
temp = 'XXX'
'''

# Get field map values from file
fieldMap = open('fieldMap.csv','r')
fieldMapValues = fieldMap.readlines()
del fieldMapValues[0]
		
distanceValues = []
fieldValues = []
		
for i in fieldMapValues:
	value = i.split(',')
	distanceValues.append(float(value[0]))
	fieldValues.append(float(value[1]))
fieldMap.close()				  
				      
# Print information about script
print("NMRshuttle.py\nVersion 3.0\nThis program is for controlling a NMR low field shuttle using a TMCM-1060 or TMCM-1160 motor.\nCopyright (c) Andrew Hall, 2019\nFor further details see https://github.com/AMRHall/NMR_Shuttle/blob/master/README.md\n\n\n")

# Import default values from setup file
setup = NMRShuttleSetup.NMRShuttle()

# Define parameters of magnet + shuttle system
B0 = setup.B0                      # Magnetic field strength at centre of magnet (Tesla)
Circ = setup.circ		   # Circumference of spindle wheel (cm)
BSample = float(sys.argv[3])	   # Sample field strength (mT)
speed = float(sys.argv[6])	   # Motor speed (cm/s)
accel = float(sys.argv[7])	   # Acceleration (cm/s^2)
dist = float(sys.argv[8])	   # Distance to move (cm)
setpoint = float(sys.argv[9])      # Setpoint temperature (K)
ramp = str(sys.argv[10])           # Equation for velocity ramp


# Open communications with motor driver
PyTrinamic.showInfo()
#PyTrinamic.showAvailableComPorts()

myInterface = serial_tmcl_interface(setup.serial)
module = TMCM_1160(myInterface)
print("\n")

# Open communications to the heater/chiller
dyneo = julaboController.dyneo(port=setup.julaboPort)

# Reset all error flags
errflag = 0
module.setUserVariable(9,0)	#Clear motor error flags
module.setUserVariable(8,0)	#Set position to 'down'


# Get operation mode
mode = int(sys.argv[1]) # 1 = Constant velocity, 2 = Velocity sweep, 3 = Constant time

# Fetch appropriate stall guard settings
stallSetting = int(sys.argv[2])
if stallSetting == 1:
	stallGuard = NMRShuttleSetup.stallGuard_1()
elif stallSetting == 2:
	stallGuard = NMRShuttleSetup.stallGuard_2()
elif stallSetting == 3:
	stallGuard = NMRShuttleSetup.stallGuard_3()
else:
	print("Invalid value for tube type.")
	sys.exit(0)

# Motor settings
module.motorRunCurrent(stallGuard.motorRunCurrent)
module.motorStandbyCurrent(stallGuard.motorStandbyCurrent)
module.stallguard2Filter(stallGuard.stallguard2Filter)
module.stallguard2Threshold(stallGuard.stallguard2Threshold)
module.stopOnStall(stallGuard.stopOnStall)
module.setAxisParameter(154,setup.pulDiv)
module.setAxisParameter(153,setup.rampDiv)

# Convert speed and acceleration from real units to motor units
pulseDiv = module.axisParameter(154)
uStepRes = module.axisParameter(140)
fullStepRot = setup.fullStepRot
rampDiv = module.axisParameter(153)
NStep = fullStepRot * 2**uStepRes

# The TMCM-1060 works in internal units of pps/s whilst the TMCM-1160 uses arbitary 12 bit internal units
# These calculations are taken from pages 91 - 95 of the TMCM-1160 manual.
if setup.model == 'TMCM-1160':
	speed = int(((speed/Circ) * fullStepRot * (2**uStepRes) * (2**pulseDiv) * 2048 * 32)/(16 * (10**6)))
	maxSpeed = int(((setup.maxSpeed/Circ) * fullStepRot * (2**uStepRes) * (2**pulseDiv) * 2048 * 32)/(16 * (10**6)))
	accel = int(((accel/Circ) * fullStepRot * (2**uStepRes) * (2**(rampDiv + pulseDiv + 29)))/((16 * (10**6))**2))
elif setup.model == 'TMCM-1060':
	speed = int((speed/Circ) * fullStepRot * (2**uStepRes))
	maxSpeed = int((setup.maxSpeed/Circ) * fullStepRot * (2**uStepRes))
	accel = int((accel/Circ) * fullStepRot * (2**uStepRes))
else:
	print("Invalid motor model.")
	sys.exit(0)
	
module.setMaxVelocity(maxSpeed)
module.setMaxAcceleration(accel)


#Print some information for the user
if mode == 1 or mode == 3:
	module.setTargetSpeed(speed)
	print("Target speed = " + str(speed))
	     
print("Acceleration = " + str(accel))

print(str("Magnetic field strength = " + str(BSample) +  " mT"))

print(str("Height = " + str(round(dist,2)) + " cm"))

    
# Calculate number of steps
steps = int((dist*NStep)/Circ)
print(str("Number of steps = " + str(steps) + "\n"))

module.setUserVariable(1,steps)


# Get number of transients for each field strength
NS = int(sys.argv[4])

# Get number of 2D slices
TD = int(sys.argv[5])
  
# Set the heater/chiller to the right temperature and wait
dyneo.switchOn()
dyneo.setTemp(round(setpoint - 273.15, 2))
time.sleep(setup.equilibTime)
	
# Check position of sample and wait until finished
up = False
newLine = False
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
		
		#If terminate signal recieved from Topspin, safely stop motor
		#signal.signal(1, terminate)
	
		#Check sample position
		position = module.userVariable(8)
		if up == False and position == 1:
			up = True
			print("\nSample UP")
			startTime = time.time()
		if up == True and position == 1:
			elapsedTime = round(time.time() - startTime,1)
			print('\rElapsed time = ' + str(elapsedTime), end = ' ')
			newLine = True
		if up == True and position == 0:
			up = False
			n += 1
			print("\nSample DOWN")
			if TD == 1:
				print(str("Completed scan " + str(n) + " of " + str(NS) + " at magnetic field strength of " + str(BSample) + " mT"))
			else:
				print(str("Completed scan " + str(n) + "/" + str(NS) + " for 2D slice " + str(m) + "/" + str(TD) + " at magnetic field strength of " + str(BSample) + " mT"))
			if mode == 2:
				print("\n")
		if position == 2 and mode == 2:
			while z < dist:
				if newLine == True:
					print('')
					newLine = False
				z = (module.actualPosition()*(setup.direction*Circ))/NStep
				Bz = np.interp(z,distanceValues,fieldValues)
				rampSpeed = int(speed*eval(ramp))
				module.setTargetSpeed(rampSpeed)
				print('\rTarget speed = ' + str(rampSpeed), end = ' ')
		time.sleep(0.02)
		
# Once sequence is complete for all magnetic field strengths:
# Set motor distance back to zero for safety
module.setUserVariable(1,0)

# Print completion message
timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
if errflag ==0:
	print(str("\nSequence successfully completed at " + str(timestamp)))
else:
	print(str("\nSequence aborted with " + str(errflag) + " error(s) at " + str(timestamp) + "\n"))

# Close serial ports
myInterface.close()
dyneo.close()

sys.exit(errflag)