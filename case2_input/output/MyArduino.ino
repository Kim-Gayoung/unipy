#include <ArduinoJson.h>
#include <Servo.h>
Servo outerServo;
int outerPin = 10;
int pos = 110;
DynamicJsonBuffer jsonBuffer;JsonObject & jsonObject ;
void setup() {
    Serial.begin(9600);
    outerServo.attach(outerPin);
}

void loop() {
    dispatch();
}

void dispatch() {
    String str = "";

    while (Serial.available() > 0) {
        str = Serial.readString();
    }
    if (str != "") {
        jsonObject = jsonBuffer.parseObject(str);
    }
    funid = jsonObject["_funid"];
    if (funid == 4) {
        servoControl();
    }
}

void servoControl() {
    String data = jsonObject["_String_data"];

    if (data == "r") {
        pos = pos - 10;
        data = 0;
        if (pos < 0) {
            pos = 0;
        }
    }
    else if (data == "l") {
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
