import os

GETCURDATA

mode = GETPAR("CNST 11")
type = GETPAR("CNST 12")
BSample = GETPAR("CNST 20")
ns = GETPAR("NS")

command = str("python3.6 user/NMRShuttle.py " + mode + " " + type + " " + BSample + " " + ns)

print(command)
os.system(command)

ZG
