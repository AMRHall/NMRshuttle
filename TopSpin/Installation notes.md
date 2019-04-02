# Instructions for installing NMRShuttle scripts for TopSpin3.5 on Linux Centos 7.
For more details contact a.m.r.hall@soton.ac.uk

## 1. Install Python
NMRShuttle requires Python 3.6 minimum. To check which version of python is installed, open a terminal window and enter:

`python3.6 --version`  

If Python 3.6 is installed then the version number should be displayed. If Python 3.6 is not installed then install this using the instructions here before continuing: https://www.rosehosting.com/blog/how-to-install-python-3-6-4-on-centos-7/ (requires admin privilages).

## 2. Install Python libraries
### 2.1. Install Pyserial
Enter the following command into the terminal window:

`python3.6 pip install --user PySerial`

(Note that this will only install for the current user. To install for all users, root permisions are required)

##### To check if the installation has succeeded:  
`python3.6`  
`import serial`

If no error messages are given, the installation was a success.

`exit()`



### 2.2. Install Git
Enter the following command into the terminal window:

`python3.6 pip install --user gitpython`

##### To check if the installation has succeeded:  
`python3.6`  
`import git`

If no error messages are given, the installation was a success.

`exit()`



### 2.3. Install motor driver
Enter the following command into the terminal window:

`python3.6 pip install --user git+https://github.com/AMRHall/PyTrinamic`

##### To check if the installation has succeeded:  
`python3.6`  
`import PyTrinamic`

If no error messages are given, the installation was a success.

`exit()`


## 3. Install TopSpin scripts
### 3.1. Download files
Go to https://github.com/AMRHall/NMRshuttle and download the folder as .zip.
Unpack the .zip folder.

### 3.2. Install scripts
Open TopSpin and enter the command `edpy` to go to the Python script libary.

Go to File > Import and from the folder that you have just downloaded select the files named:

`NMRShuttle.py`

`NMRShuttleSetup.py`

`runNMRShuttle.py`

Import these files into TopSpin.

Open the file named `runNMRShuttle.py` and check that the file path on line 3 matches the location that you have just saved the files to.

### 3.3. Install AU program
In TopSpin enter the command `edau` to go to the automation program library.

Go to File > Import and from the folder that you have just downloaded select the file named:

`zg_xpya`

Import the file into TopSpin.

### 3.4. Install pulse program
In TopSpin enter the command `edpul` to go to the pulse program library.

Go to File > Import and from the folder that you have just downloaded select the file named:

`M2SvdfS2M_trig`

Import the file into TopSpin.

## 4. Running experiments
### 4.1. Electrical connections
The NMRShuttle uses the spectrometer output TTL lines 8 and 9, located on pins C3 and C4 (AVANCE III) for triggering the motor. If different pins are used for triggering, simply change the pulse program accordingly.

A return signal that indicates when the motor is moving is currently located on spectrometer input0 (pin C5 on AVANCE III).

### 4.2. Motor settings
Settings for the motor are stored in the `NMRShuttleSetup.py` file that you saved in the TopSpin python libary. This file contains parameters for the maximum and target speed, acceleration, communication port, maximum allowed height, StallGuard settings, motor wheel circumference and velocity ramp equation.

The setup file also includes parameters describing the magnetic field strength profile of the magnet, fitted using the equation:

BSample = B0/(1+(x/b)^a)

### 4.3. Pulse program
The pulse program must include trigger out signals to tell the motor when to move up and down. The motor triggers when the pin is set low. As the motor takes a finite amount of time to move into position, it is advisable to include a delay of around 5 seconds to allow the motor to reach the correct position.

### 4.4. Acquisition parameters
* The acquisition python program (PYNM) must be set to `runNMRShuttle.py`.

* The acqusition automation program (AUNM) must be set to `zg_xpya`.

The following constants are also used to set parameters within the NMRShuttle program:

| Constant        | Value           | Meaning  |
| --- | --- | --- |
| NS     | 1...&#8734;| Number of scans for each FID |
| TD(F1)    | 1...&#8734;| Number time domain points for 2nd dimension (typically used to for variable delay in pseudo-2D spectra) |
| CNST 11    | 1...3| Operation mode for NMR Shuttle (1 = constant velocity, 2 = velocity sweep, 3 = constant time) |
| CNST 12    | 1...3| NMR tube type (1 = standard 5mm glass tube, 2 =5 mm high pressure tube, 3 = 10mm high pressure tube) |
| CNST 20    | (0)...B0| Low field strength (mT): Use this to set the field strength that you want the motor to move to. NOTE: Minimum field strength will depend on magnet and apparatus parameters. |
| CNST 30    | 0.05...30.| Specify target speed (cm/s) (optional). If no value is set (= 0 or 1) then the default value from the NMRShuttleSetup.py file will be taken.|
| CNST 31    | 0.5...465| Specify acceleration (cm/s^2) (optional). If no value is set (= 0 or 1) then the default value from the NMRShuttleSetup.py file will be taken.|
| D10    | 0...&#8734;| Sample motion time (s) (used in pulse program and constand time mode). |

### 4.5. Acquisition modes
The NMRShuttle can operate in three different modes:
1. Constant velocity (default): The sample is accelerated up to the target velocity set either in the NMRShuttleSetup file or CNST 30. The time taken to move the sample is dependant on the distance being traveled (and therefore on field strength).
2. Velocity sweep: The sample speed follows a profile that is set using the equation in USERA1. This should be of the form:

  speed = `function[curr_position]`

3. Constant speed: The time taken for the sample motion to complete remains constant over all field strengths, however the sample velocity will change depending on the distance that must be moved. The sample motion time may be set using parameter D10. If the time set in D10 is too short to allow the sample motion to complete then an error message will be displayed and the experiment will not run.

### 4.6. Starting the experiment
The NMR experiment must be started by calling the `zg_xpya` automation program, either directly by name, or using the `xaua` command. If you wish to queue multiple experiments, then the `multizg` program can be modified by replacing `zg` with `xaua` in the `multizg` program.
