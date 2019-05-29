#
# runNMRShuttle.py
# Version 1.2, Apr 2019
#
# Andrew Hall 2019 (c)
# a.m.r.hall@soton.ac.uk
#
# Python script for calling NMR low field shuttle operation and starting acquisition in Topspin.
# Includes options for different NMR tubes and for arbitarily defined velocity/distance profiles.
# Requires setup file containing motor parameters.
#


#Import libraries
import os
import math
import NMRShuttleSetup
import subprocess

setup = NMRShuttleSetup.NMRShuttle()

#Set TopSpin installation directory
path = "/opt/topspin3.5pl7/"

#Get parameters from TopSpin and NMRShuttleSetup.py
mode = int(GETPAR("CNST 11"))
tubeType = int(GETPAR("CNST 12"))
BSample = float(GETPAR("CNST 20"))
ns = int(GETPAR("NS"))
dim = int(GETPAR("PARMODE"))
motionTime = float(GETPAR("D 10"))


if str(GETPAR("USERA1")) != "":
  ramp = str(GETPAR("USERA1"))
else:
  ramp = setup.ramp

if GETPAR("CNST 30") != "1":
  speed = float(GETPAR("CNST 30"))
else:
  speed = setup.speed

if GETPAR("CNST 31") != "1":
  accel = float(GETPAR("CNST 31"))
else:
  accel = setup.accel
if (accel < 0)  or (accel > 465.434):
  value = SELECT(message = "Acceleration out of range! (CNST31)", buttons=["OVERRIDE", "CANCEL"], title="NMR Shuttle Error")
  if value == 1 or value < 0:
  	ct = XCMD("STOP")
  	EXIT()

if dim == 0:
  td = "1"
else:
  td = GETPAR("TD",1)


#Calculate distance that motor needs to move to achieve the desired field strength.
distance = float(setup.b*(((setup.B0/BSample)-1)**(1/setup.a)))
if (distance < 0)  or (distance > setup.maxHeight):
  ERRMSG("Field strength out of range! (CNST20)", modal=1, title="NMR Shuttle Error")
  ct = XCMD("STOP")
  EXIT()


#For modes 1 and 3, estimate the amount of time needed to complete sample motion. For constant time mode, calculate the speed that the motor needs to run at.
if mode == 1:
	print("\n\nConstant velocity mode")
	if (accel * (speed/accel)**2) >= distance:
		motionTime = 2 * math.sqrt(distance/accel)
	else:
		motionTime = 2 * (speed/accel) + (distance - accel*((speed/accel)**2))/speed
	PUTPAR("D 10",str(motionTime))
	
elif mode == 2:
	print("\n\nVelocity sweep mode")
	motionTime = 0
	currField = setup.B0
	currPosition = 0
	currSpeed = speed*float(eval(ramp))
	dDistance = 0
	if ramp.find("currField") != -1:
		while currField >= BSample:
			lastPosition = currPosition
			currPosition = float(setup.b*(((setup.B0/currField)-1)**(1/setup.a))) 
			dDistance = currPosition - lastPosition
			lastSpeed = currSpeed
			currSpeed = speed*float(eval(ramp))
			avgSpeed = (currSpeed + lastSpeed)/2
			motionTime += dDistance/avgSpeed
			currField -= (0.01*(setup.B0-BSample))
	elif ramp.find('currPosition') != -1:
		while currPosition <= distance:
			dDistance = 0.01*distance
			lastSpeed = currSpeed
			currSpeed = speed*float(eval(ramp))
			avgSpeed = (currSpeed + lastSpeed)/2
			motionTime += dDistance/avgSpeed
			currPosition += 0.01*distance
	else:
		ERRMSG("Invalid equation for velocity sweep ramp.\nEquation must be expressed in terms of sample position (currPosition) or local field strength (currField).", modal=1, title="NMR Shuttle Error")
		EXIT()
	PUTPAR("D 10",str(motionTime))
	
elif mode == 3:	
	print("\n\nConstant time mode") 
	if 4 * distance > accel * (motionTime**2):
		ERRMSG("Speed out of range! (CNST30)\nIncrease the sample motion time (D10).", modal=1, title="NMR Shuttle Error")
		EXIT()
	else:
		speed = 0.5 * (accel * motionTime - math.sqrt(accel) * math.sqrt(-4 * distance + accel * motionTime**2))
	PUTPAR("CNST 30",str(speed))
else:
  ERRMSG("Invalid value for operation mode (CNST11).", modal=1, title="NMR Shuttle Error")
  EXIT()


#Error messages
if tubeType == 1:
	print("Standard 5mm tube")
elif tubeType == 2:
	print("5mm high pressure tube")
elif tubeType == 3:
	print("10mm high pressure tube")
else:
	ERRMSG("Invalid value for tube type (CNST12).", modal=1, title="NMR Shuttle Error")
	EXIT()
	
if (speed < 0)  or (speed > setup.maxSpeed):
  value = SELECT(message = "Speed out of range! (CNST30)\nIf using constant time mode, consider increasing the sample motion time (D10).", buttons=["OVERRIDE", "CANCEL"], title="NMR Shuttle Error")
  if value == 1 or value < 0:
  	EXIT()
  

	
#Call NMRShuttle.py with arguments 

command = "python3.6 NMRShuttle.py "
arguments = str(mode) + " " + str(tubeType) + " " + str(BSample) + " " + str(ns) + " " + td + " " + str(speed) + " " + str(accel) + " '" + ramp + "'"

print(command + arguments)
proc = subprocess.Popen(command + arguments, cwd=path + "exp/stan/nmr/py/user", shell=True)

#Start acquisition
ct = XCMD("ZG")


#Send terminate command to motor if acqusition fails
if ct.getResult() == -1:
	proc.send_signal(signal.SIGTERM)

#Abort acquisition if motor returns an error
return_code = proc.wait()
if return_code == 0:
  ERRMSG("Acquistion completed successfully!", title="NMR Shuttle")
else:
  ct = XCMD("STOP")
  ERRMSG("Acquisition halted due to error in motor driver.", modal=1, title="NMR Shuttle Error")
