//
//
//#include "pins.h"
//
//#include <VL53L0X.h>
//#include <Wire.h>
//
//// Invert encoder directions if needed
//const boolean INVERT_ENCODER_LEFT = false;
//const boolean INVERT_ENCODER_RIGHT = false;
//
//// Invert motor directions if needed
//const boolean INVERT_MOTOR_LEFT = false;
//const boolean INVERT_MOTOR_RIGHT = false;
//
//// Loop count, used for print statements
//int count = 0;
//
//// Sensor states
//float velocity_angular = 0;
//float velocity_linear = 0;
//float left_dist;
//float right_dist;
//float center_dist;
//
//void setup() {
//  Serial.begin(9600);
//  hardwareSetup();
//}
//
//void loop() {
//  // Read sensor data
//  left_dist = getDistanceLeft();
//  right_dist = getDistanceRight();
//  center_dist = getDistanceCenter();
//
//  velocity_linear = getLinearVelocity();
//  velocity_angular = getAngularVelocity();
//  
//  ////////////////////////////////////
//  // Your changes should start here //
//  ////////////////////////////////////
//
//  float left_power = 0.2;
//  float right_power = 0.2;
//
//  applyPowerLeft(left_power);
//  applyPowerRight(right_power);
//
//  // Print debug info every 500 loops
//  if (count % 500 == 0) {
//    Serial.print(velocity_linear / 100.0);
//    Serial.print(" ");
//    Serial.print(velocity_angular);
//    Serial.print(" ");
//    Serial.print(left_dist);
//    Serial.print(" ");
//    Serial.print(center_dist);
//    Serial.print(" ");
//    Serial.print(right_dist);
//    Serial.println();
//  }
//  count++;
//
//  checkEncodersZeroVelocity();
//  updateDistanceSensors();
//}
