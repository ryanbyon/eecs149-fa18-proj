#include "pins.h"
//// Invert encoder directions if needed
//const boolean INVERT_ENCODER_LEFT = false;
//const boolean INVERT_ENCODER_RIGHT = false;
//
//// Invert motor directions if needed
//const boolean INVERT_MOTOR_LEFT = false;
//const boolean INVERT_MOTOR_RIGHT = false;

// Loop count, used for print statements
int count = 0;

const float k_left = 0.1;
const float k_right = 0.1; 
const float k_l_v = 0.001;

// Sensor states
//float velocity_angular = 0;
//float velocity_linear = 0;

//PWM values
float left_power = 0.2;
float right_power = 0.255;

// controlled values
float error = 0;
float u_right = 0;
float u_left = 0;

//distance, timing
float dist = 0;
unsigned long prev_time;
unsigned long curr_time;
unsigned long start_time;
unsigned long end_time;
int target = 0;

//flag
boolean flag = false;

void setup() {
  // put your setup code here, to run once:
  hardwareSetup();
  Serial.begin(9600);
}

void loop() { 
  // put your main code here, to run repeatedly:
  applyPowerLeft(0);
  applyPowerRight(0);
  if (Serial.available()) {
    target = Serial.parseInt();
    dist = 0;
    flag = true;
  }
  prev_time = micros();
  start_time = prev_time;
  while (dist < target) {
    velocity_linear = getLinearVelocity();
    velocity_angular = getAngularVelocity();
    velocity_left = getVelocityLeft();
    velocity_right = getVelocityRight();
    
    u_left = k_left * velocity_angular;
    u_right = k_right * (-1) * velocity_angular;  
    
    float left_power = 0.22;
    float right_power = 0.2;
    
    applyPowerLeft(left_power + u_left);
    applyPowerRight(right_power + u_right);
    
    // Print debug info every 500 loops
    if (count % 500 == 0) {
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

  if (end_time != 0 && flag) {
//    Serial.print("Time interval: ");
    Serial.print((end_time - start_time));
    Serial.print("\n");
    flag = false;
  }
}
