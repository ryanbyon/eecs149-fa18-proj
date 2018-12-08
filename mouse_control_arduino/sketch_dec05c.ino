#include "pins.h"
#include <math.h>
//// Invert encoder directions if needed
//const boolean INVERT_ENCODER_LEFT = false;
//const boolean INVERT_ENCODER_RIGHT = false;
//
//// Invert motor directions if needed
//const boolean INVERT_MOTOR_LEFT = false;
//const boolean INVERT_MOTOR_RIGHT = false;

// Loop count, used for print statements
int count = 0;

//error adjustment variable
const float k_left = 0.1;
const float k_right = 0.1; 
const float k_l_v = 0.001;

// Sensor states
//float velocity_angular = 0;
//float velocity_linear = 0;

//PWM values
//float left_power = 0.2;
//float right_power = 0.255;

// controlled values
float error = 0;
float u_right = 0;
float u_left = 0;

//distance, timing
float dist = 0;
float angle = 0;
unsigned long prev_time;
unsigned long curr_time;
unsigned long start_time;
unsigned long end_time;
int target = 0;
int target_dist = 0;
int input = 0;

// flag for whether receive angle or distance
boolean recv = true;

//flag for printing timing
boolean flag = false;

void setup() {
  // put your setup code here, to run once:
  hardwareSetup();
  Serial.begin(9600);
}

void loop() { 
  // stop the motor when no input is available
  applyPowerLeft(0);
  applyPowerRight(0);

  // if receive input from bluetooth, execute commands
  if (Serial.available()) {
      input = Serial.parseInt();
      if (input == 0) {
          dist = 0;
          angle = 0;
          count = 0;   
          flag = true;
          target= 0;
          target_dist = 0;
          Serial.println("input = 0");
          while (Serial.available()) {
            Serial.read();
            Serial.flush();
          }
    } else {
        if (recv) {
          target_dist = 0;
          target = input;
          dist = 0;
          angle = 0;
          count = 0;   
          flag = true;
          Serial.print("set degree: ");
          Serial.println(target);
        } else {
          target_dist = input;
          target = 0;
          dist = 0;
          angle = 0;
          count = 0;   
          flag = true;
          Serial.print("set distance: ");
          Serial.println(target_dist);
        }
    }
 
    recv = !recv;
    
    dist = 0;
    angle = 0;
    count = 0;   
    flag = true;

  //start the timer
  prev_time = micros();
  start_time = prev_time;

  
  if (recv == 0) {
        float tar = -1 * (float)target/180.0 * PI / 2.0;
        if (tar < 0) {
          Serial.println("turning left");
          while (angle > tar) {
            velocity_linear = getLinearVelocity();
            velocity_angular = getAngularVelocity();
            applyPowerLeft(0.23);
            applyPowerRight(-0.2);
            if (count % 50 == 0) {
              curr_time = micros();
              angle += (velocity_angular)*((float)(curr_time - prev_time)/1000000.0);
              prev_time = curr_time;
              end_time = checkEncodersZeroVelocity();
          }
           count++;  
         }
         angle = 0;
         count = 0;
        } else if (tar > 0) {
            Serial.println("turning right");
          while (angle < tar) {
            velocity_linear = getLinearVelocity();
            velocity_angular = getAngularVelocity();
            applyPowerLeft(-0.2);
            applyPowerRight(0.292);
            if (count % 50 == 0) {
              curr_time = micros();
              angle += (velocity_angular)*((float)(curr_time - prev_time)/1000000.0);
              prev_time = curr_time;
              end_time = checkEncodersZeroVelocity();
            }
            count++;
         }
         angle = 0;
         count = 0;
        } 
  } else {
      if (target_dist != 0) {
        Serial.println("going straight");
        while (dist < target_dist) {
          velocity_linear = getLinearVelocity();
          velocity_angular = getAngularVelocity();
          velocity_left = getVelocityLeft();
          velocity_right = getVelocityRight();
          
          u_left = k_left * velocity_angular;
          u_right = k_right * (-1) * velocity_angular;  
          
          float left_power = 0.2;
          float right_power = 0.2;
          
          applyPowerLeft(left_power + u_left);
          applyPowerRight(right_power + u_right);
          
          // Print debug info every 500 loops
          if (count % 50 == 0) {
            curr_time = micros();
      //      Serial.print("time: ");
      //      Serial.println(curr_time - prev_time);
            dist = dist + (velocity_linear / 100.0)*((float)(curr_time - prev_time)/1000000.0);
      //      Serial.print("distance: ");
      //      Serial.println(dist);
      //       Serial.print("target: ");
      //      Serial.println(target);
            prev_time = curr_time;
          }
      count++;
    
      end_time = checkEncodersZeroVelocity();
    }
     count = 0;
     dist = 0;
  }
  }
  
    target= 0;
    target_dist = 0;
//  if (end_time != 0 && flag) {
////    Serial.print("Time interval: ");
//    Serial.print((end_time - start_time));
//    Serial.print("\n");
//    flag = false;
//  }
    while (Serial.available()) {
      Serial.read();
      Serial.flush();
    } 
   }
}
