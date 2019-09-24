/*************************************************** 
  This script is for recording temperature with the Adafruit 
  PT100/P1000 RTD Sensor w/MAX31865 and for recording magnetic field
  with the LakeShore 2x-250-FA 2Dex Hall sensor and the Adafruit ADS1115
  Analogue to Digital converter.

  Designed specifically to work with the Adafruit RTD Sensor
  ----> https://www.adafruit.com/products/3328

  The Adafruit RTD sensor uses SPI to communicate, 4 pins are required to  
  interface (3 pins are shared bettween multiple boards)
  
  The Adafruit ADC uses SCL/SDA to communicate, 2 pins are required to interface.
  
  Adafruit invests time and resources providing this open source code, 
  please support Adafruit and open-source hardware by purchasing 
  products from Adafruit!

  Written by Limor Fried/Ladyada for Adafruit Industries. 
  Modified by Andrew Hall (University of Southampton)
  BSD license, all text above must be included in any redistribution
 ****************************************************/

#include <Adafruit_MAX31865.h>
#include <Wire.h>
#include <Adafruit_ADS1015.h>

// Set up breakout boards. Use software SPI for MAX31865: CS (unique to each board), DI (shared), DO (shared), CLK (shared)
Adafruit_MAX31865 Tsensor1 = Adafruit_MAX31865(10, 11, 12, 13);
Adafruit_MAX31865 Tsensor2 = Adafruit_MAX31865(9, 11, 12, 13);
Adafruit_MAX31865 Tsensor3 = Adafruit_MAX31865(8, 11, 12, 13);
Adafruit_ADS1115 ads;  /* Use this for the 16-bit version */

#define debug false

// Set some constants for the temperature sensors
  // The value of the Rref resistor. Use 430.0 for PT100 and 4300.0 for PT1000
  #define RREF          430.0
  // The 'nominal' 0-degrees-C resistance of the sensor (100.0 for PT100, 1000.0 for PT1000)
  #define RNOMINAL      100.0

// Set some constants for the ADC
  // The multiplier used to convert from 16 bit integer to voltage. Be sure to update this value based on the gain settings!
  #define MULTIPLIER    0.015625


void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  
  Serial.println("Adafruit MAX31865 PT100 & Adafruit ADS1115 ADC Sensor Test");
  Serial.println("ADC Range: +/- 0.512V (8x gain, 1 bit = 0.015625mV)");
  
  // The ADC input range (or gain) can be changed via the following
  // functions, but be careful never to exceed VDD +0.3V max, or to
  // exceed the upper and lower limits if you adjust the input range!
  // Setting these values incorrectly may destroy your ADC!
  //                                                                ADS1015  ADS1115
  //                                                                -------  -------
  // ads.setGain(GAIN_TWOTHIRDS);  // 2/3x gain +/- 6.144V  1 bit = 3mV      0.1875mV (default)
  // ads.setGain(GAIN_ONE);        // 1x gain   +/- 4.096V  1 bit = 2mV      0.125mV
  // ads.setGain(GAIN_TWO);        // 2x gain   +/- 2.048V  1 bit = 1mV      0.0625mV
  // ads.setGain(GAIN_FOUR);       // 4x gain   +/- 1.024V  1 bit = 0.5mV    0.03125mV
     ads.setGain(GAIN_EIGHT);      // 8x gain   +/- 0.512V  1 bit = 0.25mV   0.015625mV
  // ads.setGain(GAIN_SIXTEEN);    // 16x gain  +/- 0.256V  1 bit = 0.125mV  0.0078125mV

  // Start all sensors
  Tsensor1.begin(MAX31865_4WIRE);  // set to 2WIRE or 4WIRE as necessary
  Tsensor2.begin(MAX31865_4WIRE);  // set to 2WIRE or 4WIRE as necessary
  Tsensor3.begin(MAX31865_4WIRE);  // set to 2WIRE or 4WIRE as necessary
  ads.begin();
}

void diagnoseFault(uint8_t fault) {
  if (fault & MAX31865_FAULT_HIGHTHRESH) {
    Serial.println(":  RTD High Threshold"); 
  }
  if (fault & MAX31865_FAULT_LOWTHRESH) {
    Serial.println(":  RTD Low Threshold"); 
  }
  if (fault & MAX31865_FAULT_REFINLOW) {
    Serial.println(":  REFIN- > 0.85 x Bias"); 
  }
  if (fault & MAX31865_FAULT_REFINHIGH) {
    Serial.println(":  REFIN- < 0.85 x Bias - FORCE- open"); 
  }
  if (fault & MAX31865_FAULT_RTDINLOW) {
    Serial.println(":  RTDIN- < 0.85 x Bias - FORCE- open"); 
  }
  if (fault & MAX31865_FAULT_OVUV) {
    Serial.println(":  Under/Over voltage"); 
  }
}


void loop() {
  Serial.flush();


  // Check and print any faults in temperature sensors
  uint8_t fault1 = Tsensor1.readFault();
  if (fault1) {
    Serial.print("Sensor 1 Fault 0x"); Serial.print(fault1, HEX);
    diagnoseFault(fault1);
    Tsensor1.clearFault();
  }
    
  uint8_t fault2 = Tsensor2.readFault();
  if (fault2) {
    Serial.print("Sensor 2 Fault 0x"); Serial.print(fault2, HEX);
    diagnoseFault(fault2);
    Tsensor2.clearFault();
  }
  
  uint8_t fault3 = Tsensor3.readFault();
  if (fault3) {
    Serial.print("Sensor 3 Fault 0x"); Serial.print(fault3, HEX);
    diagnoseFault(fault3);
    Tsensor3.clearFault();
  }


  // Read ADC
  int16_t adcValue;
  float adcVoltage;
  
  adcValue = ads.readADC_Differential_0_1();
  adcVoltage = adcValue * MULTIPLIER;
  
  // Since ADC gain is limited to prrevent damage to chip at high magentic fields
  // at low magnetic fields, gain can be increased.
  if (adcVoltage < 128) {
    ads.setGain(GAIN_SIXTEEN);
    adcValue = ads.readADC_Differential_0_1();
    adcVoltage = adcValue * MULTIPLIER / 2;
    ads.setGain(GAIN_EIGHT);
  }
    
  if (debug == true) {
    Serial.print("Differential: "); Serial.println(adcValue); 
    Serial.println("("); Serial.print(adcVoltage,4); Serial.println("mV)");
  }
  
  // Print output from sensors
  Serial.print("{"); Serial.print(Tsensor1.temperature(RNOMINAL, RREF)); Serial.print(", "); Serial.print(Tsensor2.temperature(RNOMINAL, RREF)), Serial.print(", "); Serial.print(Tsensor3.temperature(RNOMINAL, RREF)); Serial.print(", "); Serial.print(adcVoltage,4); Serial.println("}");
  //  Serial.println();
  delay(500);
}
