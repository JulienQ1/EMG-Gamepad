#include "CurieIMU.h"
#include "CurieTimerOne.h"
#include <math.h>

// Initialize variables //
char incomingChar;
int counter = 0;
int interval = 5000;   // 200 Hz --> 5 ms = 5000 us

int currentTime;
int timeInit;
int timeFin;
int timeDiff;

int analogPin;
int pin = 0;

int ax, ay, az;
int gx, gy, gz;
float ax2, ay2, az2, am;
float gy2, gz2;

float emgVoltage;
float voltUnit = 3.3 / 1024;
float voltOffset = 1.5;
float scaleUnit = 3600 / 1000;

float hpOut;
float lpOut;
float rectOut;
float boxOut;

int accelRange = 2;
int gyroRange = 250;

int startTime1 = 0;
int startTime2 = 0;

float threshold_mV = 0.15;
float threshold_time_emg = 700000;
float threshold_time_gyro = 800000;
float threshold_accel = 1.5;
float threshold_gyro = 200;

// Boxcar filter function //
float boxcarFilter(float sample) {
  static const int boxcarWidth = 10;    // Change this value to alter boxcar length
  static float recentSamples[boxcarWidth] = {0};    // hold onto recent samples
  static int readIndex = 0;     // the index of the current reading
  static float total = 0;     // the running total
  static float average = 0;     // the average

  // subtract the last reading:
  total = total - recentSamples[readIndex];
  
  // add new sample to list (overwrite oldest sample)
  recentSamples[readIndex] = sample;
  
  // add the reading to the total:
  total = total + recentSamples[readIndex];
  
  // advance to the next position in the array:
  readIndex = readIndex + 1;

  // if we're at the end of the array...
  if (readIndex >= boxcarWidth) {
    // ...wrap around to the beginning:
    readIndex = 0;
  }

  // calculate the average:
  average = total / boxcarWidth;
  
  // send it to the computer as ASCII digits
  return average;
}

// High pass filter function //
float highPassFilter(float sample) {
  static const float a[4] = {1.00000000, -2.37409474, 1.92935567, -0.53207537};     // ADD A VALUES HERE
  static const float b[4] = {0.72944072, -2.18832217, 2.18832217, -0.72944072};     // ADD B VALUES HERE

  // x array for holding recent inputs (newest input as index 0, delay of 1 at index 1, etc.
  static float x[4] = {0};
  
  // x array for holding recent inputs (newest input as index 0, delay of 1 at index 1, etc.
  static float y[4] = {0};

  x[0] = sample;

  // Calculate the output filtered signal based on a weighted sum of previous inputs/outputs
  y[0] = (b[0]*x[0]+b[1]*x[1]+b[2]*x[2]+b[3]*x[3])-(a[1]*y[1]+a[2]*y[2]+a[3]*y[3]);
  y[0] /= a[0];

  // Shift the input signals by one timestep to prepare for the next call to this function
  x[3] = x[2];
  x[2] = x[1];
  x[1] = x[0];

  // Shift the previously calculated output signals by one time step to prepare for the next call to this function
  y[3] = y[2];
  y[2] = y[1];
  y[1] = y[0];

  return y[0];
}

// Low pass filter function //
float lowPassFilter(float sample) {
  static const float a[4] = {1.00000000e+00, -2.77555756e-16, 3.33333333e-01, -1.85037171e-17};     // ADD A VALUES HERE
  static const float b[4] = {0.16666667, 0.50000000, 0.50000000, 0.16666667};     // ADD B VALUES HERE

  // x array for holding recent inputs (newest input as index 0, delay of 1 at index 1, etc.
  static float x[4] = {0};
  
  // x array for holding recent inputs (newest input as index 0, delay of 1 at index 1, etc.
  static float y[4] = {0};

  x[0] = sample;

  // Calculate the output filtered signal based on a weighted sum of previous inputs/outputs
  y[0] = (b[0]*x[0]+b[1]*x[1]+b[2]*x[2]+b[3]*x[3])-(a[1]*y[1]+a[2]*y[2]+a[3]*y[3]);
  y[0] /= a[0];

  // Shift the input signals by one timestep to prepare for the next call to this function
  x[3] = x[2];
  x[2] = x[1];
  x[1] = x[0];

  // Shift the previously calculated output signals by one time step to prepare for the next call to this function
  y[3] = y[2];
  y[2] = y[1];
  y[1] = y[0];

  return y[0];
}

float rectify(float sample){
  if(sample < 0){
    sample = sample * (-1);
  }
  return sample;
}

// Function that scales raw integer samples into millivolts //
float scaleVolts(int rawVal){
  float voltage;
  voltage = voltUnit * rawVal;
  voltage = (voltage - voltOffset) / scaleUnit;
  return voltage;
}

float convertAccel(float aRaw){
    float accelScaled = ((aRaw / 32768.0) * accelRange);
    return accelScaled;
}

float convertGyro(float gRaw){
    float gyroScaled = ((gRaw / 32768.9) * gyroRange);
    return gyroScaled;
}

// Function that prints out sensor readings //
void printValues(float val){
  Serial.print(" ");
  Serial.print(val);
}

void printInts(int val){
  Serial.print(" ");
  Serial.print(val);
}

void printVal3(int val1, int val2, int val3){
  Serial.print(" ");
  Serial.print(val1);
  Serial.print(" ");
  Serial.print(val2);
  Serial.print(" ");
  Serial.print(val3);
}

// Function that reads sensor values from analog pins //
void sample(void){
  // Print time //
  currentTime = micros();
//  Serial.print(currentTime);

  // Print processed analog signal //
  analogPin = analogRead(pin);
  emgVoltage = scaleVolts(analogPin);
  hpOut = highPassFilter(emgVoltage);
  lpOut = lowPassFilter(hpOut);
  rectOut = rectify(lpOut);
  boxOut = boxcarFilter(rectOut);
//  printValues(boxOut);

  // Print accelerometer //
  CurieIMU.readAccelerometer(ax, ay, az);
  ax2 = convertAccel(ax);
  ay2 = convertAccel(ay);
  ay2 = convertAccel(ay);
  am = pow(pow(ax2, 2) + pow(ay2, 2) + pow(az2, 2), 0.5);
//  Serial.print(am);
//  Serial.print(" ");

  // Print gyroscope //
  CurieIMU.readGyro(gx, gy, gz);
  gy2 = convertGyro(gy);
  gz2 = convertGyro(gz);

//  Serial.print(gy2);
//  Serial.print(" ");
//  Serial.println(gz2);

  if(startTime1 == 0 || micros() - startTime1 > threshold_time_emg){
    if(boxOut > threshold_mV){
      Serial.println("U");
      startTime1 = micros();
    }
  }
  
  if(am > threshold_accel){
    if(startTime2 == 0 || micros() - startTime2 > threshold_time_gyro){
      if((gy2 > threshold_gyro) && (gy2 > 0)){
        Serial.println("R");
        startTime2 = micros();
      }
      if((gy2*(-1) > threshold_gyro) && (gy2 < 0)){
        Serial.println("L");
        startTime2 = micros();
      }

      if(gz2 > threshold_gyro){
        Serial.println("B");
        startTime2 = micros();
      }
    }
  }
    
}

void setup() {
  Serial.begin(115200);
  while (!Serial);      // Wait for serial monitor to open
  CurieIMU.begin();
  CurieIMU.setAccelerometerRange(2);
  CurieIMU.setGyroRange(250);
  CurieTimerOne.start(interval, &sample);
}

void loop() {
  ;
}
