#include <Servo.h>
Servo outerServo;
int outerPin = 10;
int pos = 110;
int receivedAscii = 0;
char data = "";
void dispatch() {
    int funid = "";

    if (Serial.available() > 0) {
        funid = Serial.read();
    }
    if (funid == 5) {
        servoControl();
    }
}
void setup() {
    Serial.begin(9600);
    outerServo.attach(outerPin);
}
void loop() {
    servoControl(data);
}
void servoControl() {
    data = Serial.read();
    if (receivedAscii == 114) {
        pos = pos - 10;
        receivedAscii = 0;
        if (pos < 0) {
            pos = 0;
        }
    }
    outerServo.write(pos);
}
