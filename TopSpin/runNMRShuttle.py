import os
import math
import NMRShuttleSetup

setup = NMRShuttleSetup.NMRShuttle()

#Set directory to TopSpin python user library
os.chdir("/opt/topspin3.5pl7/exp/stan/nmr/py/user")

#Get parameters from TopSpin
mode = GETPAR("CNST 11")
type = GETPAR("CNST 12")
BSample = GETPAR("CNST 20")
ns = GETPAR("NS")
dim = GETPAR("PARMODE")
speed = GETPAR("CNST 30")
accel = GETPAR("CNST 31")
setTime = GETPAR("D10")
if dim != 0:
  td = GETPAR("TD",1)
else:
  td = 1
  
distance = float(setup.b*(((setup.B0/BSample)-1)**(1/setup.a)))

#Error messages
if mode != 1 or mode != 2 or mode !=3:
  ERRMSG("Invalid value for operation mode (CNST11).",modal=1)
  ct = XCMD("STOP")
  EXIT()
  
if type != 1 or mode != 2 or mode !=3:
  ERRMSG("Invalid value for tube type (CNST12).",modal=1)
  ct = XCMD("STOP")
  EXIT()

if (distance < 0)  or (distance > setup.maxHeight):
  ERRMSG("Field strength out of range! (CNST20)",modal=1)
  ct = XCMD("STOP")
  EXIT()
	
  
#If mode = constant time, calculate the speed that the motor needs to run at.
if mode == 3:
  speed = 0.5 * (accel * setTime - math.sqrt(accel) * math.sqrt(-4 * distance + accel * setTime**2))
  if 4 * distance > accel * (setTime**2):
    ERRMSG("Speed out of range! (CNST30)\nIncrease the sample motion time (D10).",modal=1)
    ct = XCMD("STOP")
    EXIT()

if (accel < 0)  or (accel > 465.434):
  ERRMSG("Acceleration out of range! (CNST31)",modal=1)
  ct = XCMD("STOP")
  EXIT()
	
if (speed < 0)  or (accel > 30.5027):
  ERRMSG("Speed out of range! (CNST30)\nIf using constant time mode, consider increasing the sample motion time (D10).",modal=1)
  ct = XCMD("STOP")
  EXIT()
  
	
#Call NMRShuttle.py with arguments  
command = str("python3.6 NMRShuttle.py " + mode + " " + type + " " + BSample + " " + ns + " " + td + " " + speed + " " + accel)

print(command)
os.system(command)

