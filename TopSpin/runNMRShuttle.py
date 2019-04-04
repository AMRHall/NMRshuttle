import os
import math
import NMRShuttleSetup

setup = NMRShuttleSetup.NMRShuttle()

#Set directory to TopSpin python user library
os.chdir("/opt/topspin3.5pl7/exp/stan/nmr/py/user")

#Get parameters from TopSpin
mode = int(GETPAR("CNST 11"))
type = int(GETPAR("CNST 12"))
BSample = GETPAR("CNST 20")
ns = GETPAR("NS")
dim = GETPAR("PARMODE")
speed = float(GETPAR("CNST 30"))
accel = float(GETPAR("CNST 31"))
setTime = GETPAR("D10")
ramp = str(GETPAR("USERA 1"))
if dim != 0:
  td = GETPAR("TD",1)
else:
  td = 1
  
distance = float(setup.b*(((setup.B0/float(BSample))-1)**(1/setup.a)))

#For mode 3 calculate motor speed.
if mode == (1 or 2):
  time = setTime
#If mode = constant time, calculate the speed that the motor needs to run at.
elif mode == 3:
  speed = 0.5 * (accel * setTime - math.sqrt(accel) * math.sqrt(-4 * distance + accel * setTime**2))
  if 4 * distance > accel * (setTime**2):
    ERRMSG("Speed out of range! (CNST30)\nIncrease the sample motion time (D10).",modal=1)
    ct = XCMD("STOP")
    EXIT()
else:
  ERRMSG("Invalid value for operation mode (CNST11).",modal=1)
  ct = XCMD("STOP")
  EXIT()

#Error messages
if type != (1 or 2 or 3):
  ERRMSG("Invalid value for tube type (CNST12).",modal=1)
  ct = XCMD("STOP")
  EXIT()

if (distance < 0)  or (distance > setup.maxHeight):
  ERRMSG("Field strength out of range! (CNST20)",modal=1)
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
command = str("python3.6 NMRShuttle.py " + str(mode) + " " + str(type) + " " + BSample + " " + ns + " " + td + " " + str(speed) + " " + str(accel) + " " + ramp)

print(command)
os.system(command)

