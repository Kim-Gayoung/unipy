#include <Servo.h>
Servo outerServo;
int outerPin = 10;
int pos = 110;
char data = "";
void setup() {
    Serial.begin(9600);
    outerServo.attach(outerPin);
}
void loop() {
    dispatch();
}
void dispatch() {
    char funid = "";

    if (Serial.available() > 0) {
        funid = Serial.read();
    }
    if (funid == 4) {
        servoControl();
    }
}
void servoControl() {
    data = Serial.read();
    if (data == 114) {
        pos = pos - 10;
        data = 0;
        if (pos < 0) {
            pos = 0;
        }
    }
    outerServo.write(pos);
}
