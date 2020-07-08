/*
NMRshuttle
Flow direction relay

Arduino relay to control solenoid valves for temperature control
fluid flow direction. Uses Arduino A000110 Arduino Quad Relay.
Relays automatically switch direction after set delay. TTL trigger 
from spectrometer blocks the relay for 10 seconds to prevent the 
flow direction switching during acquisition.

Delay for switching can be sent to arduino using the command 'D XX'
where XX is the delay time in seconds. Sending the command '?' returns
the current status of the valves; 0= de-energised, 1= energised.

(c) Andrew Hall 2020
a.m.r.hall@ed.ac.uk

version 1.0
Jul 2020
*/


bool debug = false;


// define pins used by relay shield
const int relay1 = 4;
const int relay2 = 7;
const int relay3 = 8;
const int relay4 = 12;
const int ttl = A0;


// Variables that will change:
int valveState = LOW;             // valveState used to set the valve
int switchDelay = 60;             // default value for valve switching delay
bool hold = false;                // hold state used to prevent switching during acquisition
int holdDelay = 10;               // delay to prevent switching during acquisition


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
}



void loop() {
  
  // if there's any serial available, read it:
  while (Serial.available() > 0) {
    
    String line = Serial.readStringUntil('\n');
    
    // check to see if status request from computer
    if (line.indexOf("?") >= 0) {
      Serial.print("STATUS: ");
      Serial.println(valveState);
    }
    
    // if serial input is an integer, store this as the switching delay
    else if (line.toInt() > 0) {
      switchDelay = line.toInt();
      
      Serial.print("DELAY: ");
      Serial.println(switchDelay);
    }
  }
  
  
  
  // check to make sure spectrometer hasn't triggered acquisition to start
  // if it has then start the holding delay.
  // Note that Bruker spectrometers use active low logic.
  if (analogRead(ttl) < 500) {
    if (hold == false && debug == true){
      Serial.println("Start hold");
    }  
    hold = true;
    holdStart = millis();
  } 
  
  
  // get current time in milliseconds
  unsigned long currentMillis = millis();
  
  
  // if in hold mode wait for the hold delay to end
  if (hold == true) {
    if (currentMillis - holdStart >= (holdDelay*1000)) {
      hold = false;
      if (debug == true) { 
        Serial.println("End hold");
      }
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
      
    // set the relays with the valveState of the variable:
    digitalWrite(LED_BUILTIN, valveState);
    digitalWrite(relay3, valveState);
    digitalWrite(relay4, valveState);
  }
}
