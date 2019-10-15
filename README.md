# NMR Shuttle

Andrew Hall &#169; 2019

a.m.r.hall@soton.ac.uk

Python script for controlling NMR low field shuttle with Trinamic TMCM-1060 or TMCM-1160 motor.
Includes options for different NMR tubes and for arbitarily defined velocity/distance profiles.
Requires setup file containing motor parameters and VBlist file containing list of field strengths 
to be installed in same directory as this python script. Also requires PyTrinamic and Serial libraries.


## Contents:
__Arduino__
* ___NMRShuttle_Sensors.ino___ (Firmware for Arduino sensor logger)

__Python__
* ___fieldMap.py___ (Python program for automatically recording a field map profile using a hall sensor and stepper motor)
* ___sensorShield.py___ (Python program for reading sensor data from Arduino. Includes GUI for plotting data in real time)

__TMCL__
* ___NMRShuttle_1060_v4.tmc___ (Firmware for TMCM-1060 stepper motor)
* ___NMRShuttle_1160_v4.tmc___ (Firmware for TMCM-1160 stepper motor)

__TopSpin__
* __Pulse Programs__ - These files should be loaded into the pulse program library (accessed using _'edpul'_)
  * ___M2SvdfS2M___ (2D pulse sequence for T<sub>s</sub> measurement)
  * ___M2SvdfS2M-1d___ (1D pulse sequence for T<sub>s</sub> measurement)
  * ___M2SvdfS2M-1d_trig___ (1D pulse sequence for T<sub>s</sub>  measurement with variable field shuttle)
  * ___M2SvdfS2M_trig___ (2D pulse sequence for T<sub>s</sub>  measurement with variable field shuttle)
  * ___sd25M2SvdfS2M___ (2D pulse sequence for T<sub>s</sub>  measurement with singlet destruction)
  * ___sd25M2SvdfS2M_trig___ (2D pulse sequence for T<sub>s</sub>  measurement with variable field shuttle and singlet destruction)
  * ___t1ir___ (2D T<sub>1</sub> pulse sequence).
  * ___t1ir_trig___ (2D T<sub>1</sub> pulse sequence with trigger for variable field shuttle).
  
* __Python__ - These files should be loaded into the TopSpin python libary (accessed using _'edpy'_)
  * ___Dyneo.py___ (Python program for setting temperature of heater/chiller)
  * ___NMRShuttle.py___ (Python program for controlling shuttle motor unit)
  * ___NMRShuttleSetup.py___ (Setup and default parameters for NMR Shuttle program)
  * ___julaboController.py___ (Python program for interfacing with heater/chiller)
  * ___runNMRShuttle.py___ (Python script enabling TopSpin to interface with motor unit)
  * ___zg_xpya___ (Python script for executing acquisition without triggering motor)
  
__Installation notes__

__License file__

__README__
   
