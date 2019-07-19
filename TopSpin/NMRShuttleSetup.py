'''
Created on 21.03.2019
@author: AH
'''

class NMRShuttle(object):

  # Serial port name for motor
  serial =            "/dev/ttyACM0"
  
  # Motor model
  model =             "TMCM-1160"
  
  # Motor direction
  direction =         -1

  # Maximum allowed height (cm)
  maxHeight =         90

  # Magnetic field strength at magnet core (mT)
  B0 =                7056.390197

  # Circumference of motor wheel (cm)
  circ =              25.0

  # Number of steps for full revolution of motor
  fullStepRot =       200



  # Target motor speed (cm/s) (0...30.518 with default settings)
  speed =             25

  # Maximum motor acceleration (cm/s^2) (0...465.5 with default settings). This can be adapted by changing motor rampDiv setting or motor wheel diameter
  accel =             22.74

  # Maximum motor speed (cm/s) (0...30.518 with default settings). This can be adapted by changing motor pulDiv setting or motor wheel diameter
  maxSpeed =          30.518

  # Velocity ramp equation. Equation must be expressed as a Python math equation in terms of sample position (z) or local field strength (Bz)
  ramp =              "1-0.9/(1+math.exp(-0.001*(Bz-5000)))"


  
# Settings for low field homogeneity coil. If coil is not used, set lowFieldCoil_Field to 0 or NaN.
  # Field strength (mT)
  lowFieldCoil_Field= 1.0
  
  # Distance of coil from centre of magnet (cm)
  lowFieldCoil_Dist = 150.0
  
  
  # Offset distance of Hall sensor from sample
  offsetDist =        20.0
  
  
# *****************************
# THE FOLLOWING PARAMETERS CAN BE DANGEROUS IF CHANGED. DO NOT ALTER THEM UNLESS YOU KNOW WHAT YOU ARE DOING!
# *****************************

  # Motor pulse division (0...13). DO NOT CHANGE THIS NUMBER UNLESS YOU HAVE READ THE MANUAL! 
  # Changes maximum speed of motor. Decreasing the number increases speed, but compromises precision.
  pulDiv =          3
  
  # Motor ramp division (0...13). DO NOT CHANGE THIS NUMBER UNLESS YOU HAVE READ THE MANUAL! 
  # The exponent of the scaling factor for the ramp generator.
  rampDiv =         7
  
 


# *****************************
# STALL GUARD SETTINGS ARE USED TO LIMIT THE TORQUE THAT THE MOTOR CAN APPLY.
# SEE THE MANUAL FOR MORE DETAILS.
# *****************************

class stallGuard_1(object):
  # Stall guard setting 1
  motorRunCurrent =         64
  motorStandbyCurrent =     16
  stallguard2Filter =       1
  stallguard2Threshold =    4
  stopOnStall =             1000

class stallGuard_2(object):
  # Stall guard setting 2
  motorRunCurrent =         64
  motorStandbyCurrent =     16
  stallguard2Filter =       1
  stallguard2Threshold =    4
  stopOnStall =             1000

class stallGuard_3(object):
  # Stall guard setting 3
  motorRunCurrent =         80
  motorStandbyCurrent =     16
  stallguard2Filter =       1
  stallguard2Threshold =    8
  stopOnStall =             1000

