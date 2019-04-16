/*
  Temperature and field logging

  Reads the value of a thermocouple on analog input pin, 
  maps the result to a range from 0 to 255 and prints the results to the Serial Monitor.

  created 16 Apr 2019
  by Andrew Hall
  A.M.R.Hall@soton.ac.uk

*/

// These constants won't change. They're used to give names to the pins used:
const int TSens1 = A0;  // Analog input pin that thermocouple 1 is attached to
const int TSens2 = A1;  // Analog input pin that thermocouple 2 is attached to
const int TSens3 = A2;  // Analog input pin that thermocouple 3 is attached to

int sensorValue1 = 0;        // value read from the port
int sensorValue2 = 0;        // value read from the port
int sensorValue3 = 0;        // value read from the port



//Linear temperature calibration. 
//Resistance per degC (ohms):
const float TCal1 = 38.5;
const float TCal2 = 38.5;
const float TCal3 = 38.5;

//Zero degree reference (ohms):
const float zeroRef1 = 100;
const float zeroRef2 = 100;
const float zeroRef3 = 100;

//Reference resistor (ohms):
const float RRef = 100;



void setup() {
  // initialize serial communications at 9600 bps:
  Serial.begin(9600);
}

void loop() {
  // read the analog in value:
  sensorValue1 = analogRead(TSens1);
  sensorValue2 = analogRead(TSens2);
  sensorValue3 = analogRead(TSens3);

  float temp1 = ((RRef/((5/(sensorValue1*0.0049))-1))-zeroRef1)/TCal1;
  float temp2 = ((RRef/((5/(sensorValue2*0.0049))-1))-zeroRef2)/TCal2;
  float temp3 = ((RRef/((5/(sensorValue3*0.0049))-1))-zeroRef1)/TCal3;
  
  
  // print the results to the Serial Monitor:
  Serial.print("Temperatures = " + String(temp1) + ", " + String(temp2) + ", " + String(temp3) + "\n");

  // wait 2 milliseconds before the next loop for the analog-to-digital
  // converter to settle after the last reading:
  delay(2);
}
