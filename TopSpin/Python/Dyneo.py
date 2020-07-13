"""
Dyneo.py
Author: Andrew Hall
Version: 2.0
Updated: Jul 2020

Acts as a bridge between Topspin and julaboController.py, allowing serial
communication for control of Julabo heater/chiller and flow direction valves.
"""

import julaboController
import sys, time


# Import dyneo module
dyneo = julaboController.dyneo()

# Attempt to import flow direction valve module.
# If no response then print error and continue.
try:
    valves = julaboController.valves()
except:
    print('ERROR: Communication with flow direction valves failed')
    valves_disabled = True
else:
    valves_disabled = False



# Check arguments from Topspin. Switch on and set temperature and flow 
# switching delay accordingly. If argument is 'OFF' switch everything off.
if sys.argv[1] == 'OFF':
	dyneo.switchOff()
	if valves_disabled == False:
		valves.switchOff()
	print('Dyneo off')
	
else:
    if valves_disabled == False:
        if sys.argv[2] == 'OFF':    
            valves.switchOff()
            print("Flow direction valves: " + valves.checkStatus().strip('\n'))
        else:
            valves.switchOn()
            valves.setDelay(float(sys.argv[2]))
            print('Flow direction switching delay: ' + sys.argv[2])
            print("Flow direction valves: " + valves.checkStatus().strip('\n'))
    dyneo.switchOn()
    time.sleep(1)   # delay to allow Julabo time to respond
    dyneo.setTemp_wait(float(sys.argv[1]))


# Close serial communication
dyneo.close()
if valves_disabled == False:
    valves.close()
