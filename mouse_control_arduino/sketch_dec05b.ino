//
//
//#include "pins.h"
//
//// Invert encoder directions if needed
////const boolean INVERT_ENCODER_LEFT = false;
////const boolean INVERT_ENCODER_RIGHT = false;
////
////// Invert motor directions if needed
////const boolean INVERT_MOTOR_LEFT = false;
////const boolean INVERT_MOTOR_RIGHT = false;
//
//// Loop count, used for print statements
//int count = 0;
//
//const float k_left = 0.1;
//const float k_right = 0.1; 
//// Sensor states
////float velocity_angular = 0;
////float velocity_linear = 0;
////float left_dist;
////float right_dist;
////float center_dist;
//
//float error = 0;
//float u_right = 0;
//float u_left = 0;
//void setup() {
//  Serial.begin(9600);
//  hardwareSetup();
//}
//
//char data = '0';
//void loop() {
//  // Read sensor data
////  left_dist = getDistanceLeft();
////  right_dist = getDistanceRight();
////  center_dist = getDistanceCenter();
//if (Serial.available()) {
//  data = Serial.read();
//}
//
//if (data == '0') {
//  applyPowerLeft(0);
//  applyPowerRight(0);
//} else {
//  velocity_linear = getLinearVelocity();
//  velocity_angular = getAngularVelocity();
//  velocity_left = getVelocityLeft();
//  velocity_right = getVelocityRight();
//  
//  ////////////////////////////////////
//  // Your changes should start here //
//  ////////////////////////////////////
//
//  u_left = k_left * velocity_angular;
//  u_right = k_right * (-1) * velocity_angular;  
//  
//  float left_power = 0.22;
//  float right_power = 0.2;
//  
//  applyPowerLeft(left_power + u_left);
//  applyPowerRight(right_power + u_right);
//
//  // Print debug info every 500 loops
//  if (count % 500 == 0) {
////    Serial.print(String(left_power));
////    Serial.print("\t");
//////    Serial.print(String(velocity_linear / 100.0));
////    Serial.print(String(velocity_left / 100.0));
////    Serial.print("\t");
////    Serial.print(String(velocity_right / 100.0));
////    Serial.print("\t");
////    Serial.print(String(velocity_angular));
////    Serial.print("\n");
////    Serial.print(left_dist);
////    Serial.print(" ");
////    Serial.print(center_dist);
////    Serial.print(" ");
////    Serial.print(right_dist);
////    Serial.println();
//  }
//  count++;
//
//  checkEncodersZeroVelocity();
////  updateDistanceSensors();
//}
//}
