#include <Wire.h>        // ✅ Ensure Wire library is included
#include "HCPCA9685.h"   // ✅ Include HCPCA9685 library

#define I2CAdd 0x40  // PCA9685 I2C Address

/* Create PCA9685 object */
HCPCA9685 HCPCA9685(I2CAdd);

/* Define min and max PWM values for 250° servo */
#define SERVO_MIN 10    // PWM value for 0 degrees
#define SERVO_MAX 450   // PWM value for 250 degrees

// Store current servo positions (default to midpoint)
int servoPos[6] = {125, 125, 125, 125, 125, 30};  

int incomingByte = 0;  
char whichAxis = '\0';
char token[10];
int tokenPos = 0;

/* Function to convert degrees (0-250) to PCA9685 PWM values */
int angleToPWM(int angle) {
    return map(angle, 0, 250, SERVO_MIN, SERVO_MAX);
}

/* Function to move a servo to the desired angle */
void moveDegrees(int servoIndex, double degrees) {
    if (servoIndex < 0 || servoIndex > 5) return;

    int max_angle = (servoIndex == 4 || servoIndex == 5) ? 130 : 250;
    int angle = constrain((int)degrees, 0, max_angle);

    if (servoIndex == 2) {
        angle = max_angle - angle; // Invert elbow servo if necessary
    }

    servoPos[servoIndex] = angle;
    int pwmValue = angleToPWM(angle);
    HCPCA9685.Servo(servoIndex, pwmValue);  // ✅ Use correct HCPCA9685 function

    Serial.print("Servo ");
    Serial.print(servoIndex);
    Serial.print(" -> ");
    Serial.print(angle);
    Serial.println(" degrees");
}

/* Function to read serial input and control servos */
void readSerial() {
    if (Serial.available()) {
        incomingByte = Serial.read();  

        if (incomingByte != ' ' && incomingByte != '\n') {
            if (whichAxis == '\0') {
                whichAxis = incomingByte;  
            } else {
                token[tokenPos++] = (char)incomingByte;
            }
        } else {
            token[tokenPos] = '\0';
            double distance = atof(token);
            int servoIndex = whichAxis - '0';  

            moveDegrees(servoIndex, distance);

            whichAxis = '\0';
            tokenPos = 0;
        }
    }
}

/* Move all servos to neutral position (125°) */
void moveAllToNeutral() {
    Serial.println("Moving all servos to 125 degrees...");
    for (int i = 0; i < 6; i++) {
        if (i == 2) {
            moveDegrees(i, 125);
        } else {
            moveDegrees(i, 125);
        }
    }
    Serial.println("All servos set to neutral position.");
}

/* Arduino setup function */
void setup() {
    Serial.begin(9600);
    Wire.begin();    // ✅ Explicitly start I2C communication

    /* Initialize PCA9685 in Servo Mode */
    HCPCA9685.Init(SERVO_MODE);
    HCPCA9685.Sleep(false);  // Wake up the device

    moveAllToNeutral();
}

/* Main loop function */
void loop() {
    readSerial();
}
