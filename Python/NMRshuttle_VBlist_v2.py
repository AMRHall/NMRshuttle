# Import libraries and define functions
import serial
import time
import datetime

def split_hex(value,n,m):
    value = "{0:0{1}x}".format(value,n)
    value = "0x" + ",0x".join(value[i:i+2] for i in range(m, m+2, 2))
    return int(value,16)

def send_data(AD,CN,TN,MN,NV):
    
    # Define individal bytes to be sent to the motor driver
    byte0 = AD
    byte1 = CN
    byte2 = TN
    byte3 = MN
    byte4 = split_hex(NV,8,0)
    byte5 = split_hex(NV,8,2)
    byte6 = split_hex(NV,8,4)
    byte7 = split_hex(NV,8,6)
    byte8 = 0   #Checksum
    
    # Define byte list to be sent to motor driver
    bytelist = [byte0,byte1,byte2,byte3,byte4,byte5,byte6,byte7]
    
    # Checksum calculation
    for x in bytelist:
       byte8 += x
    byte8 = split_hex(byte8,8,6)
    
    # Add checksum to byte list
    bytelist.append(byte8)
    
    # Send command to motor
    ser.write(bytes(bytelist))
    ser.read(9)
	
# Import default values from setup file
setup = open("NMRshuttle_setup.txt","r").read()

# open serial port
port = (setup.split('serial: ')[1].split('\n')[0])
ser = serial.Serial(port,timeout=20)  

# Reset all error flags
errflag = 0
ser.write(bytes([0x01,0x09,0x09,0x02,0x00,0x00,0x00,0x00,0x15]))
ser.read(9)
time.sleep(0.1)


# Define parameters of magnet + shuttle system
MaxHeight = float((setup.split('MaxHeight: ')[1].split('\n')[0]))        # Maximum height of sample (cm)
B0 = float((setup.split('B0: ')[1].split('\n')[0]))                # Magnetic field strength at centre of magnet (Tesla)
a = float((setup.split('a: ')[1].split('\n')[0]))                   # Magnetic field fitting parameter 1 
b = float((setup.split('b: ')[1].split('\n')[0]))                     # Magnetic filed fitting parameter 2
Circ = float((setup.split('Circ: ')[1].split('\n')[0]))		         # Circumference of spindle wheel (cm)
NStep = int((setup.split('NStep: ')[1].split('\n')[0]))       # Number of steps for one full revolution of motor
speed = int((setup.split('speed: ')[1].split('\n')[0]))         # Target motor speed
accel = int((setup.split('accel: ')[1].split('\n')[0]))        # Motor acceleration


# Set motor speed
AD = 1      #Address (always 1)
CN = 5      #Command number (5=Set Axis Parameter, 9=Set Global Parameter, 28=STOP)
TN = 2      #Type number (Parameter number, eg. SAP 2 for set speed, SAP 5 for accelleration)
MN = 0      #Motor number (Bank number)
NV = speed  #Number value 

send_data(AD,CN,TN,MN,NV)

# Set motor acceleration
AD = 1      #Address (always 1)
CN = 5      #Command number (5=Set Axis Parameter, 9=Set Global Parameter, 28=STOP)
TN = 5      #Type number (Parameter number, eg. SAP 2 for set speed, SAP 5 for accelleration)
MN = 0      #Motor number (Bank number)
NV = accel  #Number value 

send_data(AD,CN,TN,MN,NV)


# Open file with list of magnetic field strength
VBlist = open("VBlist.txt","r").read().splitlines()

# Get number of transients for each field strength
NS = int(input("Number of transients at each magnetic field strength:"))

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
    
	# Define motor command
	AD = 1      #Address (always 1)
	CN = 9      #Command number (5=Set Axis Parameter, 9=Set Global Parameter, 28=STOP)
	TN = 1      #Type number (Parameter number, eg. SAP 2 for set speed, SAP 5 for accelleration)
	MN = 2      #Motor number (Bank number)
	NV = steps  #Number value 
    
	send_data(AD,CN,TN,MN,NV)
    
	time.sleep(0.1)
    
	# Check position of sample and wait until finished
	n = 0
	up = 'n'
	while n < NS:	
		# Check for errors in motor
	    ser.write(bytes([0x01,0x0a,0x09,0x02,0x00,0x00,0x00,0x00,0x16]))
	    error = ser.read(9)
	    time.sleep(0.1)
	    if error == b'\x02\x01d\n\x00\x00\x00\x01r':       #Shutdown error from light gate
	        print("\n\nEmergency stop detected. Aborting acquisition.")
	        errflag += 1
	        break
	    elif error == b'\x02\x01d\n\x00\x00\x00\x02s':       #Stall detected
	        print("\n\nStall detected. Aborting acquisition.")
	        errflag += 1
	        break
		
		#Check sample position
	    ser.write(bytes([0x01,0x0a,0x08,0x02,0x00,0x00,0x00,0x00,0x15]))
	    position = ser.read(9)
	    time.sleep(0.1)
	    if up == 'n' and position == b'\x02\x01d\n\x00\x00\x00\x01r':
	        up = 'y'
	        print("Sample up")
	    if up == 'y' and position == b'\x02\x01d\n\x00\x00\x00\x00q':
	        up = 'n'
	        n += 1
	        print("Sample down")
	        print("Completed transient", n, "of", NS, "at magnetic field strength of", BSample, "mT")

			
# Once sequence is complete for all magnetic field strengths:
# Set motor distance back to zero for safety
ser.write(bytes([0x01,0x09,0x01,0x02,0x00,0x00,0x00,0x00,0x0d]))
timeout = ser.read(9)
time.sleep(0.1)

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