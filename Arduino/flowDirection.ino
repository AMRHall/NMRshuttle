/*
NMRshuttle
Flow direction relay

Arduino relay to control solenoid valves for temperature control
fluid flow direction. Uses Arduino A000110 Arduino Quad Relay.
Relays automatically switch direction after set delay. TTL trigger 
from spectrometer blocks the relay for 10 seconds to prevent the 
flow direction switching during acquisition.

Delay for switching can be sent to arduino as interger values in 
seconds. Sending the command 'STATUS' returns the current status 
(ON, OFF, HOLD, ERROR). The command 'POS' returns the postion of 
the valves (1= ON, 0= OFF). The valve position can be set manually
using the commands 'SET_VALVE_ON' and 'SET_VALVE_OFF'. The module
is activated and deactivated using the commands 'SWITCH_ON' and 
'SWITCH_OFF'.

(c) Andrew Hall 2020
a.m.r.hall@ed.ac.uk

version 1.1
Jul 2020
*/


// define pins used by relay shield
const int relay1 = 4;
const int relay2 = 7;
const int relay3 = 8;
const int relay4 = 12;
const int ttl = A0;


// Variables that will change:
bool ttl_working = true;          // status of ttl input line
bool on = true;                   // module on/off state
int valveState = LOW;             // valveState used to set the valve
int switchDelay = 60;             // default value for valve switching delay
bool hold = false;                // hold state used to prevent switching during acquisition
int holdDelay = 10;               // delay to prevent switching during acquisition
String errs;                      // string for holding error messages


// Generally, you should use "unsigned long" for variables that hold time
// The value will quickly become too large for an int to store
unsigned long previousMillis = 0;        // will store last time valve was switched
unsigned long holdStart = 0;             // will store start time for hold



void setup() {
  // initialize serial:
  Serial.begin(9600);
  // make the pins outputs:
  pinMode(relay1, OUTPUT);
  pinMode(relay2, OUTPUT);
  pinMode(relay3, OUTPUT);
  pinMode(relay4, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  
  // TTL input should be high when module switched on (active low logic)
  // if no signal is detected return error message.
  if (analogRead(ttl) < 500) {
    ttl_working = false;
    errs += "ERROR: No signal from TTL input";
  }
}



void loop() {
  
  // if there's any serial available, read it:
  while (Serial.available() > 0) {
    
    String line = Serial.readStringUntil('\n');
    
    // check for switch on request
    if (line.indexOf("SWITCH_ON") >= 0) {
      on= true;
      Serial.println("ON");
    }
    
    // check for switch off request
    else if (line.indexOf("SWITCH_OFF") >= 0) {
      on= false;
      valveState = LOW;
      setPosition(valveState);
      Serial.println("OFF");
    }
    
    // check for set valve position on request
    else if (line.indexOf("SET_VALVE_ON") >= 0) {
      valveState = HIGH;
      setPosition(valveState);
      Serial.println(valveState);
    }
    
    // check for set valve position off request
    else if (line.indexOf("SET_VALVE_OFF") >= 0) {
      valveState = LOW;
      setPosition(valveState);
      Serial.println(valveState);
    }
    
    // check for status request
    else if (line.indexOf("STATUS") >= 0) {
      if (on == false) {
        Serial.println("OFF");
      }
      else if (errs.length() > 0) {
        Serial.println(errs);
      }
      else if (hold == true) {
        Serial.println("HOLD");
      }
      else {
        Serial.println("ON");
      }
    }
    
    // check for position request
    else if (line.indexOf("POS") >= 0) {
      Serial.println(valveState);
    }
    
    // if serial input is an integer, store this as the switching delay
    else if (line.toInt() > 0) {
      switchDelay = line.toInt();
      Serial.print("DELAY: ");
      Serial.println(switchDelay);
    }
  }
  
  
  if (on == true) {
    // check to make sure spectrometer hasn't triggered acquisition to start
    // if it has then start the holding delay. If no input was detected on the
    // TTL line when the module was started then this step is skipped.
    // Note that Bruker spectrometers use active low logic.
    if (analogRead(ttl) < 500 && ttl_working == true) { 
      hold = true;
      holdStart = millis();
    } 
    
    
    // get current time in milliseconds
    unsigned long currentMillis = millis();
    
    
    // if in hold mode wait for the hold delay to end
    if (hold == true) {
      if (currentMillis - holdStart >= (holdDelay*1000)) {
        hold = false;
      }
    }
    
    
    // otherwise check to see if it's time to switch the valve; that is, if the 
    // difference between the current time and last time you switched the valve is 
    // bigger than the switching time delay.
    else if (currentMillis - previousMillis >= (switchDelay*1000)) {
      
      previousMillis = currentMillis;
    
      // if the valves are off turn them on and vice-versa:
      if (valveState == LOW) {
        valveState = HIGH;
      } else {
        valveState = LOW;
      }
        
      setPosition(valveState);
    }
  }
}

void setPosition(int state) {
  // set the relays with the valveState of the variable:
    digitalWrite(LED_BUILTIN, state);
    digitalWrite(relay3, state);
    digitalWrite(relay4, state);
}
