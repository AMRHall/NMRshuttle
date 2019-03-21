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
speed = GETPAR("CNST10")				         # Target motor speed
ramp = int((setup.split('ramp: ')[1].split('\n')[0]))         # Equation for velocity ramp

PyTrinamic.showInfo()
PyTrinamic.showAvailableComPorts()

# For usb connection
port = (setup.split('serial: ')[1].split('\n')[0])
myInterface = serial_tmcl_interface(port)

module = TMCM_1160(myInterface)

# Get operation mode
mode = GETPAR("CNST11") # 1 = Constant velocity, 2 = Velocity sweep
if mode != (1 or 2):
  ERRMSG("Invalid value for operation mode.", modal=1)
  break

# Get tube type
type = GETPAR("CNST12") # 1 = Standard glass tube, 2 = 5mm High pressure tube, 3 = 10mm High pressure tube
if mode != (1 or 2 or 3):
  ERRMSG("Invalid value for tube type.", modal=1)
  break

# Motor settings
module.setMaxVelocity(int((setup.split('maxspeed: ')[1].split('\n')[0])))
module.setMaxAcceleration(int((setup.split('accel: ')[1].split('\n')[0])))

module.motorRunCurrent(int((setup.split(str(type)+'_motorRunCurrent: ')[1].split('\n')[0])))
module.motorStandbyCurrent(int((setup.split(str(type)+'_motorStandbyCurrent: ')[1].split('\n')[0])))
module.stallguard2Filter(int((setup.split(str(type)+'_stallguard2Filter: ')[1].split('\n')[0])))
module.stallguard2Threshold(int((setup.split(str(type)+'_stallguard2Threshold: ')[1].split('\n')[0])))
module.stopOnStall(int((setup.split(str(type)+'_stopOnStall: ')[1].split('\n')[0])))

if mode == 1:
  module.setTargetSpeed(speed)

# Reset all error flags
errflag = 0
module.setUserVariable(9,0)

# Get number of transients for each field strength
NS = GETPAR("NS")

# Check for error flags
if errflag != 0:
	break

# Fetch desired magnetic field strength (mT)
BSample = GETPAR("CNST20")
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
	break
    
# Calculate number of steps
steps = int((dist*NStep)/Circ)
status_msg = str("Number of steps =", steps)
print(status_msg)

module.setUserVariable(1,steps)
  
# Check position of sample and wait until finished
n = 0
up = 'n'
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
		start_position = module.actualPosition()
	if up == 'y' and position == 0:
		up = 'n'
		n += 1
		status_msg = str("Sample down in ", elapsed_time, " seconds.")
		SHOW_STATUS(status_msg)
		status_msg = str("Completed transient", n, "of", NS, "at magnetic field strength of", BSample, "mT")
		SHOW_STATUS(status_msg)
		start_position = module.actualPosition()
	start_time = time.time()
	while position == 2 and mode == 2:
		curr_position = ((module.actualPosition() - start_position)*Circ)/NStep
		speed = eval(ramp)
		module.setTargetSpeed(speed)
		elapsed_time = start_time - time.time()
	while position == 2 and mode != 2:
		elapsed_time = start_time - time.time()
		
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
