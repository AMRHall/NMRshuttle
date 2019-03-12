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
acceleration = int((setup.split('accel: ')[1].split('\n')[0]))        # Target motor acceleration


PyTrinamic.showInfo()
PyTrinamic.showAvailableComPorts()

# For usb connection
port = (setup.split('serial: ')[1].split('\n')[0])
myInterface = serial_tmcl_interface(port)

module = TMCM_1160(myInterface)

# Motor settings
module.setMaxVelocity(int((setup.split('maxspeed: ')[1].split('\n')[0])))
module.setMaxAcceleration(int((setup.split('maxaccel: ')[1].split('\n')[0])))
module.motorRunCurrent(int((setup.split('motorRunCurrent: ')[1].split('\n')[0])))
module.motorStandbyCurrent(int((setup.split('motorStandbyCurrent: ')[1].split('\n')[0])))
module.stallguard2Filter(int((setup.split('stallguard2Filter: ')[1].split('\n')[0])))
module.stallguard2Threshold(int((setup.split('stallguard2Threshold: ')[1].split('\n')[0])))
module.stopOnStall(int((setup.split('stopOnStall: ')[1].split('\n')[0])))
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
  
  module.setUserVariable(1,steps)
  
  # Check position of sample and wait until finished
	n = 0
	up = 'n'
	while n < NS:	
		# Check for errors in motor
		error = module.userVariable(9)
		if error == 1:		#Shutdown error from light gate
			print("\n\nEmergency stop detected. Aborting acquisition.")
	        	errflag += 1
	        	break
		elif error == 2:       #Stall detected
	        	print("\n\nStall detected. Aborting acquisition.")
	        	errflag += 1
	        	break
			
		#Check sample position
		position = module.userVariable(8)
			if up == 'n' and position == 1:
				up = 'y'
				print("Sample up")
			if up == 'y' and position == 0:
	        		up = 'n'
	        		n += 1
	        		print("Sample down")
	        		print("Completed transient", n, "of", NS, "at magnetic field strength of", BSample, "mT")
			
# Once sequence is complete for all magnetic field strengths:
# Set motor distance back to zero for safety
module.setUserVariable(1,0)

# Print competion message
timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
if errflag ==0:
	print("\nSequence successfully completed at", timestamp)
else:
	print("\nSequence aborted with", errflag, "error(s) at", timestamp)

# Exit program
exit = input("Exit program (Y/N):")
if exit =="Y" or exit =="y":
	print("Exiting program...")
	time.sleep(1)

	# Close serial port
	ser.close()
