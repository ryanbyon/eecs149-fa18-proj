//#include "pins.h"
////// Invert encoder directions if needed
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
//// Sensor states
////float velocity_angular = 0;
////float velocity_linear = 0;
//
////PWM values
//float left_power = 0;
//float right_power = 0;
//  
//void setup() {
//  // put your setup code here, to run once:
//  hardwareSetup();
//  Serial.begin(9600);
//}
//
//void loop() { 
//  // put your main code here, to run repeatedly:
//
//  velocity_linear = getLinearVelocity();
//  velocity_angular = getAngularVelocity();
//  velocity_left = getVelocityLeft();
//  velocity_right = getVelocityRight();
//  
//
//   if (left_power >= 0.4) {
//      left_power = 0;
//      right_power = 0;
//    }
//  applyPowerLeft(left_power);
//  applyPowerRight(right_power);
//  
//  // Print debug info every 500 loops
//  if (count % 500 == 0) {
//    Serial.print(String(left_power));
//    Serial.print("\t");
////    Serial.print(String(velocity_linear / 100.0));
//    Serial.print(String(velocity_left / 100.0));
//    Serial.print("\t");
//    Serial.print(String(velocity_right / 100.0));
//    Serial.print("\t");
//    Serial.print(String(velocity_angular));
//    Serial.print("\n");
////    Serial.print(" ");
////    Serial.print(left_dist);
////    Serial.print(" ");
////    Serial.print(center_dist);
////    Serial.print(" ");
////    Serial.print(right_dist);
////    Serial.println();
//  }
//
//  if (count == 5000) {
//    left_power = left_power + 0.01;
//    right_power = right_power + 0.01;
//    count = 0;
//  }
//  count++;
//
//  checkEncodersZeroVelocity();
//}
