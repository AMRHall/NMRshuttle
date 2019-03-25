import os

os.chdir("/opt/topspin3.5pl7/exp/stan/nmr/py/user")

mode = GETPAR("CNST 11")
type = GETPAR("CNST 12")
BSample = GETPAR("CNST 20")
ns = GETPAR("NS")
dim = GETPAR("PARMODE")
if dim != 0:
  td = GETPAR("TD",1)
else:
  td = 1

command = str("python3.6 NMRShuttle.py " + mode + " " + type + " " + BSample + " " + ns + " " + td)

print(command)
os.system(command)

