#include <ArduinoJson.h>

#include <Servo.h>

Servo outerServo;

int outerPin = 10;
int pos = 110;
DynamicJsonBuffer jsonBuffer;

void setup() {
    Serial.begin(9600);

    outerServo.attach(outerPin);
}

void loop() {
    dispatch();
}

void dispatch() {
    String str = "";

    int funid = 0;

    while (Serial.available() > 0) {
        str = Serial.readString();

    }
    if (str != "") {
        JsonObject& jsonObject = jsonBuffer.parseObject(str);
        funid = jsonObject["_funid"];
    }

    if (funid == 4) {
        servoControl();
    }
}

void servoControl() {
    String recieveData = "";

    while (Serial.available() > 0) {
        recieveData = Serial.readString();

    }
    String data;

    if (recieveData != "") {
        JsonObject& jsonObject = jsonBuffer.parseObject(recieveData);
        data = jsonObject["args0"];
    }

    if (data == "r") {
        pos = pos - 10;
        data = "";
        if (pos < 0) {
            pos = 0;
        }
    }
    else if (data == "l") {
        pos = pos + 10;
        data = "";
        if (pos > 180) {
            pos = 180;
        }
    }
    else {
        
    }

    outerServo.write(pos);
}
