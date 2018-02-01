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

    if (Serial.available() > 0) {
        str = Serial.readStringUntil('\n');
    }

    if (str != "") {
        JsonObject& jsonObject = jsonBuffer.parseObject(str);
        funid = jsonObject["_funid"];
    }

    if (funid == 4) {
        servoControl();
    }

    funid = -1;
}

void servoControl() {
    String recieveData = Serial.readStringUntil('\n');

    String data;

    if (recieveData != "") {
        JsonObject& recieveJson = jsonBuffer.parseObject(recieveData);
        String tmp0 = recieveJson["args0"];
        data = tmp0;
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
