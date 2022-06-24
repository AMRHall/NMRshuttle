#
# runNMRShuttle.py
# Version 1.7, Jun 2022
#
# Andrew Hall 2022 (c)
# a.m.r.hall@ed.ac.uk
#
# Python script for calling NMR low field shuttle operation and starting acquisition in Topspin.
# Includes options for different NMR tubes and for arbitarily defined velocity/distance profiles.
# Requires setup file containing motor parameters.
#
# Input argument 'popt' will prompt user to enter number of experiments.
#


#Import libraries
import os, math, time, subprocess, sys
import NMRShuttleSetup

setup = NMRShuttleSetup.NMRShuttle()

def interp(x, x_arr, y_arr):
	for i, xi in enumerate(x_arr):
		if xi >= x:
			break    
	else:
		return None
	if i == 0:
		return None
	x_min = x_arr[i-1]
	y_min = y_arr[i-1]
	y_max = y_arr[i]
	factor = (x - x_min) / (xi - x_min)
	return y_min + (y_max - y_min) * factor 

#Set TopSpin installation directory
path = "/opt/topspin3.5pl7/"

#Open file containing experimental field map
fieldMap = open(path+'exp/stan/nmr/py/user/fieldMap.csv', 'r') #Change the path here to the correct location of the field map file
distanceValues = []
fieldValues = []
fieldMapValues = fieldMap.readlines()
del fieldMapValues[0]		#Remove header line
for i in fieldMapValues:
	value = i.split(',')
	distanceValues.append(float(value[0]))
	fieldValues.append(float(value[1]))
fieldMap.close()

#Get parameters from TopSpin and NMRShuttleSetup.py
mode = int(GETPAR("CNST 11"))		#Operation mode: 1=Constant speed, 2=Variable speed, 3=Constant time
stallSetting = int(GETPAR("CNST 12"))	#Sets which stall guard settings from setup file to use
BSample = float(GETPAR("CNST 20"))	#Target field strength (mT)
ns = int(GETPAR("NS"))			#Number of scans
dim = int(GETPAR("PARMODE"))		#Spectrum dimensions (1D, 2D...)
motionTime = float(GETPAR("D 10"))	#Time taken for sample motion (s)
setpoint = float(GETPAR("TE"))		#Temperature (K)
flowSwitchDelay = float(GETPAR("D 30"))	#Delay for flow direction switching (s)

#Get ramp equation used for variable speed experiments
if str(GETPAR("USERA1")) != "":
	ramp = str(GETPAR("USERA1"))
else:
	ramp = setup.ramp

#Check if user has set a speed, if not use default
if GETPAR("CNST 30") != "0":
	speed = float(GETPAR("CNST 30"))	
else:
	print("No target speed set by user (CNST30). If using constant time mode target speed will be calculated, otherwise default value from setup file will be used.")
	speed = setup.speed
	PUTPAR("CNST 30",str(speed))

#Check if user has set an acceleration rate, if not use default. Make sure it is within the limits of the motor.
if GETPAR("CNST 31") != "0":
	accel = float(GETPAR("CNST 31"))
else:
	print("No acceleration set by user (CNST31). Default value from setup file will be used.")
	accel = setup.accel
	PUTPAR("CNST 31",str(accel))
max_accel = setup.circ*((1.024*10**13)/(2**(setup.rampDiv+setup.pulDiv+29)))
if (accel < 0) or (accel > max_accel):
	value = SELECT(message = "Acceleration value (CNST31) out of range!/n Acceleration must be between 0 and " + str(round(max_accel,2)),
                buttons=["OVERRIDE", "CANCEL"], title="NMR Shuttle Error")
	if value == 1 or value < 0:
  		ct = XCMD("STOP")
  		EXIT()
		
#For multi-dimensional experiments get number of points in F1 dimension
if dim == 0:
	td = "1"
else:
	td = GETPAR("TD",1)
    
if "popt" in sys.argv:
    result = INPUT_DIALOG(title="NMR Shuttle", 
                          header="Number of experiments for POPT:", 
                          values=[td])
    td = result[0]


#Calculate distance that motor needs to move to achieve the desired field strength.
if BSample == setup.lowFieldCoil_Field:
	distance = setup.lowFieldCoil_Dist
elif BSample == setup.B0:
	distance = 0
else:
	distance = interp(BSample,fieldValues[::-1],distanceValues[::-1])
if (distance < 0) or (distance > setup.maxHeight):
	ERRMSG("Field strength out of range! (CNST20)", modal=1, title="NMR Shuttle Error")
	ct = XCMD("STOP")
	EXIT()

print('\n\n----------------------------------------------------')

#For constant velocity and velocity sweep modes, estimate the amount of time needed to complete sample motion. 
#For constant time mode, calculate the speed that the motor needs to run at.
if mode == 1:
	print("Constant velocity mode")
	if (accel * (speed/accel)**2) >= distance:
		motionTime = 2 * math.sqrt(distance/accel)
	else:
		motionTime = 2 * (speed/accel) + (distance - accel*((speed/accel)**2))/speed
	PUTPAR("D 10",str(motionTime))
	
elif mode == 2:		#NB. Calculations in this mode assume a high acceleration rate
	print("Velocity sweep mode")
	motionTime = 0
	Bz = setup.B0
	z = 0
	currSpeed = speed*float(eval(ramp))
	dDistance = 0
	if ramp.find("Bz") != -1:
		while Bz >= BSample:
			lastZ = z
			z = interp(Bz,fieldValues[::-1],distanceValues[::-1])
			dDistance = z - lastZ
			lastSpeed = currSpeed
			currSpeed = speed*float(eval(ramp))
			avgSpeed = (currSpeed + lastSpeed)/2
			motionTime += dDistance/avgSpeed
			Bz -= (0.01*(setup.B0-BSample))
	elif ramp.find('z') != -1:
		while z <= distance:
			dDistance = 0.01*distance
			lastSpeed = currSpeed
			currSpeed = speed*float(eval(ramp))
			avgSpeed = (currSpeed + lastSpeed)/2
			motionTime += dDistance/avgSpeed
			z += 0.01*distance
	else:
		ERRMSG("Invalid equation for velocity sweep ramp.\nEquation must be expressed in terms of sample position (z) or local field strength (currField).", modal=1, title="NMR Shuttle Error")
		EXIT()
	PUTPAR("D 10",str(motionTime))
	
elif mode == 3:	
	print("Constant time mode") 
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
if stallSetting == 1:
	print("Stall setting 1")
elif stallSetting == 2:
	print("Stall setting 2")
elif stallSetting == 3:
	print("Stall setting 3")
else:
	ERRMSG("Invalid value for stall setting (CNST12).", modal=1, title="NMR Shuttle Error")
	EXIT()
if setup.maxSpeed > setup.circ*(9.765625/(2**setup.pulDiv)):
	ERRMSG("Maximum speed out of range!\nCheck the settings in the setup file.", modal=1, title="NMR Shuttle Error")
	EXIT()
if (speed < 0)  or (speed > setup.maxSpeed):
	value = SELECT(message = "Speed out of range! (CNST30)\nIf using constant time mode, consider increasing the sample motion time (D10).", 
                buttons=["OVERRIDE", "CANCEL"], title="NMR Shuttle Error")
	if value == 1 or value < 0:
		EXIT()
  		
#Set temperature and wait for ready
command = "python3.6 Dyneo.py "
if flowSwitchDelay == 0:    # 0 is interpreted as an infinite delay (ie. valves do not switch)
	flowSwitchDelay = 'OFF'
elif flowSwitchDelay < 30:  # Minimum delay is 30s to avoid valves switching too quickly
	ERRMSG("Flow direction switching delay (D30) too short. Must be minimum 30 seconds.\nTo disable flow direction switching set D30 to zero.", 
        title="NMR Shuttle", modal=1)
	EXIT()   
arguments = str(round(setpoint-273, 2)) + " " + str(flowSwitchDelay)

if "NO_TEMP" in sys.argv:
	ERRMSG("Temperature control disabled by user", title="NMR Shuttle")
else:
	try:
		print(command + arguments)
		setTemp = subprocess.check_call(command + arguments, cwd=path + "exp/stan/nmr/py/user", shell=True)
	except:
		ERRMSG("Dyneo heater/chiller not found. Temperature will not be controlled.", title="NMR Shuttle")
	else:
		print(' Waiting for temperature to equilibriate...\n')
		time.sleep(setup.equilibTime)


#Call NMRShuttle.py with arguments 
command = "python3.6 NMRShuttle.py "
arguments = str(mode) + " " + str(stallSetting) + " " + str(BSample) + " " + str(ns) + " " + td + " " + str(speed) + " " + str(accel) + " " + str(distance) + " '" + ramp + "'"
print(command + arguments)
proc = subprocess.Popen(command + arguments, cwd=path + "exp/stan/nmr/py/user", shell=True, stdin=subprocess.PIPE)

#Start acquisition
zg = ZG(wait=NO_WAIT_TILL_DONE)


#Send terminate to motor if acquisition fails/Abort acquisition if motor returns an error
while zg.getResult() != 0:
	if proc.poll() > 0:
		ct = XCMD("STOP")
		ERRMSG("Acquisition halted due to error in motor driver.", modal=1, title="NMR Shuttle Error")
		EXIT()

if proc.poll() != 0:
	proc.communicate(b'STOP')
	ERRMSG("Acquistion stopped by Topspin.", title="NMR Shuttle", modal=1)
else:
	ERRMSG("Acquistion completed successfully!", title="NMR Shuttle", modal=0)
		
