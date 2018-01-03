#include <Servo.h>
Servo outerServo;
int outerPin = 10;
int pos = 110;
void setup() {
    Serial.begin(9600);
    outerServo.attach(outerPin);
}
void loop() {
    dispatch();
}
void dispatch() {
    int funid = 1;

    String str = '';

    while (Serial.available() > 0) {
        char c = Serial.read();

        if (c == '\n') {
            break;
        }
        else {
            str += c;
        }

    }
    funid = str.toInt();
    if (funid == 4) {
        servoControl();
    }
}
void servoControl() {
    char data = Serial.read();

    if (data == 'r') {
        pos = pos - 10;
        data = 0;
        if (pos < 0) {
            pos = 0;
        }
    }
    else if (data == 'l') {
        pos = pos + 10;
        data = 0;
        if (pos > 180) {
            pos = 180;
        }
    }
    else {
        
    }

    outerServo.write(pos);
}
