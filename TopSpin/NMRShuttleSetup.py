'''
Created on 21.03.2019
@author: AH
'''

class NMRShuttle(object):

  # Serial port name for motor
  serial =            "/dev/ttyACM0"

  # Maximum allowed height (cm)
  maxHeight =         90

  # Magnetic field strength at magnet core (mT)
  B0 =                7056.39197

  # Fitting parameters for NMR field map [equation of the form BSample = B0/(1+(x/b)^a)]
  a =                 5.75
  b =                 20.34

  # Circumference of motor wheel (cm)
  circ =              25

  # Number of steps for full revolution of motor
  NStep =             51200



  # Target motor speed (0...2047)
  speed =             1677

  # Motor acceleration (0...2047) 1099 is approximately 2000 steps/second^2 (pps^2)
  accel =             100

  # Maximum motor speed (0...2047). Max speed approx. 42 cm/second.
  maxSpeed =          2047

  # Velocity ramp equation
  ramp =              "100 + 5 * currposition"



class stallGuard_stan(object):
  # Stall guard settings for standard glass tube
  motorRunCurrent =         64
  motorStandbyCurrent =     16
  stallguard2Filter =       1
  stallguard2Threshold =    4
  stopOnStall =             1000

class stallGuard_HP5(object):
  # Stall guard settings for 5mm high pressure tube
  motorRunCurrent =         64
  motorStandbyCurrent =     16
  stallguard2Filter =       1
  stallguard2Threshold =    4
  stopOnStall =             1000

class stallGuard_HP10(object):
  # Stall guard settings for 10mm high pressure tube
  motorRunCurrent =         80
  motorStandbyCurrent =     16
  stallguard2Filter =       1
  stallguard2Threshold =    8
  stopOnStall =             1000

