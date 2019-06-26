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

#define debug true

// Set some constants for the temperature sensors
  // The value of the Rref resistor. Use 430.0 for PT100 and 4300.0 for PT1000
  #define RREF          430.0
  // The 'nominal' 0-degrees-C resistance of the sensor (100.0 for PT100, 1000.0 for PT1000)
  #define RNOMINAL      100.0

// Set some constants for the ADC
  // The multiplier used to convert from 16 bit integer to voltage. Be sure to update this value based on the gain settings!
  #define MULTIPLIER    0.015625
  // The nominal sensitivit of the hall probe sensor (mV/T). 
  #define SENSITIVITY   51.5
  // The zero-field offset of the hall probe sensor (mV).
  #define OFFSET        0.0
  // The value of the resistor used for current measurement (Ohms).
  #define RCURRENT      218.96


void setup() {
  Serial.begin(9600);
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


void loop() {
  Serial.flush();
  
// Read temperature sensor 1
  uint16_t rtd1 = Tsensor1.readRTD();
  if (debug == true) {
    Serial.print("Sensor 1 RTD value: "); Serial.println(rtd1);
    float ratio1 = rtd1;
    ratio1 /= 32768;
    Serial.print("Sensor 1 Ratio = "); Serial.println(ratio1,8);
    Serial.print("Sensor 1 Resistance = "); Serial.println(RREF*ratio1,8);
    Serial.print("Sensor 1 Temperature = "); Serial.println(Tsensor1.temperature(RNOMINAL, RREF));
  }
  // Check and print any faults
  uint8_t fault1 = Tsensor1.readFault();
  if (fault1) {
    Serial.print("Sensor 1 Fault 0x"); Serial.print(fault1, HEX);
    if (fault1 & MAX31865_FAULT_HIGHTHRESH) {
      Serial.println(":  RTD High Threshold"); 
    }
    if (fault1 & MAX31865_FAULT_LOWTHRESH) {
      Serial.println(":  RTD Low Threshold"); 
    }
    if (fault1 & MAX31865_FAULT_REFINLOW) {
      Serial.println(":  REFIN- > 0.85 x Bias"); 
    }
    if (fault1 & MAX31865_FAULT_REFINHIGH) {
      Serial.println(":  REFIN- < 0.85 x Bias - FORCE- open"); 
    }
    if (fault1 & MAX31865_FAULT_RTDINLOW) {
      Serial.println(":  RTDIN- < 0.85 x Bias - FORCE- open"); 
    }
    if (fault1 & MAX31865_FAULT_OVUV) {
      Serial.println(":  Under/Over voltage"); 
    }
    Tsensor1.clearFault();
  }
  
// Read temperature sensor 2 
  uint16_t rtd2 = Tsensor2.readRTD();
  if (debug == true) {
    Serial.print("Sensor 2 RTD value: "); Serial.println(rtd2);
    float ratio2 = rtd2;
    ratio2 /= 32768;
    Serial.print("Sensor 2 Ratio = "); Serial.println(ratio2,8);
    Serial.print("Sensor 2 Resistance = "); Serial.println(RREF*ratio2,8);
    Serial.print("Sensor 2 Temperature = "); Serial.println(Tsensor2.temperature(RNOMINAL, RREF));
  }
  // Check and print any faults
  uint8_t fault2 = Tsensor2.readFault();
  if (fault2) {
    Serial.print("Sensor 2 Fault 0x"); Serial.print(fault2, HEX);
    if (fault2 & MAX31865_FAULT_HIGHTHRESH) {
      Serial.println(":  RTD High Threshold"); 
    }
    if (fault2 & MAX31865_FAULT_LOWTHRESH) {
      Serial.println(":  RTD Low Threshold"); 
    }
    if (fault2 & MAX31865_FAULT_REFINLOW) {
      Serial.println(":  REFIN- > 0.85 x Bias"); 
    }
    if (fault2 & MAX31865_FAULT_REFINHIGH) {
      Serial.println(":  REFIN- < 0.85 x Bias - FORCE- open"); 
    }
    if (fault2 & MAX31865_FAULT_RTDINLOW) {
      Serial.println(":  RTDIN- < 0.85 x Bias - FORCE- open"); 
    }
    if (fault2 & MAX31865_FAULT_OVUV) {
      Serial.println(":  Under/Over voltage"); 
    }
    Tsensor2.clearFault();
  }

// Read temperature sensor 3
  uint16_t rtd3 = Tsensor3.readRTD();
  if (debug == true) {
    Serial.print("Sensor 3 RTD value: "); Serial.println(rtd3);
    float ratio3 = rtd3;
    ratio3 /= 32768;
    Serial.print("Sensor 3 Ratio = "); Serial.println(ratio3,8);
    Serial.print("Sensor 3 Resistance = "); Serial.println(RREF*ratio3,8);
    Serial.print("Sensor 3 Temperature = "); Serial.println(Tsensor3.temperature(RNOMINAL, RREF));
  }
  // Check and print any faults
  uint8_t fault3 = Tsensor3.readFault();
  if (fault3) {
    Serial.print("Sensor 3 Fault 0x"); Serial.print(fault3, HEX);
    if (fault3 & MAX31865_FAULT_HIGHTHRESH) {
      Serial.println(":  RTD High Threshold"); 
    }
    if (fault3 & MAX31865_FAULT_LOWTHRESH) {
      Serial.println(":  RTD Low Threshold"); 
    }
    if (fault3 & MAX31865_FAULT_REFINLOW) {
      Serial.println(":  REFIN- > 0.85 x Bias"); 
    }
    if (fault3 & MAX31865_FAULT_REFINHIGH) {
      Serial.println(":  REFIN- < 0.85 x Bias - FORCE- open"); 
    }
    if (fault3 & MAX31865_FAULT_RTDINLOW) {
      Serial.println(":  RTDIN- < 0.85 x Bias - FORCE- open"); 
    }
    if (fault3 & MAX31865_FAULT_OVUV) {
      Serial.println(":  Under/Over voltage"); 
    }
    Tsensor3.clearFault();
  }

// Read ADC
  int16_t adcValue;
  float adcVoltage;

  int16_t currValue;
  float current;

  float fieldStrength;
  
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

  currValue = ads.readADC_Differential_2_3();
  current = (-currValue * MULTIPLIER)/RCURRENT;

  fieldStrength = 1000* (((adcVoltage/current)-OFFSET)/SENSITIVITY);
    
  if (debug == true) {
    Serial.print("Differential: "); Serial.println(adcValue); 
    Serial.print("("); Serial.print(adcVoltage,4); Serial.println("mV)");
    Serial.print("Current: "); Serial.print(current,4); Serial.println("mA");
    Serial.print("Field strength: "); Serial.print(fieldStrength); Serial.println(" mT");
  }
  
// Print output from sensors
  Serial.print("{"); Serial.print(Tsensor1.temperature(RNOMINAL, RREF)); Serial.print(", "); Serial.print(Tsensor2.temperature(RNOMINAL, RREF)), Serial.print(", "); Serial.print(Tsensor3.temperature(RNOMINAL, RREF)); Serial.print(", "); Serial.print(fieldStrength); Serial.println("}");
//  Serial.println();
  delay(1000);
}
