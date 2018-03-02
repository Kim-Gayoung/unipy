#include <ArduinoJson.h>

#include <Servo.h>

Servo outerServo;

int outerPin = 10;
int pos = 110;
int doorPin = 2;
int preState = LOW;
int postState = LOW;
DynamicJsonBuffer jsonBuffer;

void setup() {
    Serial.begin(9600);

    outerServo.attach(outerPin);

    pinMode(doorPin, INPUT);
}

void loop() {
    dispatch_Serial();

    readDoorSensor();
}

void dispatch_Serial() {
    String str = "";

    int funid = 0;

    if (Serial.available() > 0) {
        str = Serial.readStringUntil('\n');
    }

    if (str != "") {
        JsonObject& jsonObject = jsonBuffer.parseObject(str);
        funid = jsonObject["_funid"];
    }

    if (funid == 14) {
        servoControl();
    }

    funid = -1;
}

void readDoorSensor() {
    postState = digitalRead(doorPin);

    if (postState == HIGH && preState == LOW) {
        JsonObject& sendFunid = jsonBuffer.createObject();
        sendFunid["_funid"] = 10;
        sendFunid.printTo(Serial);
        JsonObject& jsonObject = jsonBuffer.createObject();
        jsonObject["args0"] = 0;
        jsonObject.printTo(Serial);
        jsonBuffer.clear();
        preState = postState;
    }

    if (postState == LOW && preState == HIGH) {
        JsonObject& sendFunid = jsonBuffer.createObject();
        sendFunid["_funid"] = 10;
        sendFunid.printTo(Serial);
        JsonObject& jsonObject = jsonBuffer.createObject();
        jsonObject["args0"] = 1;
        jsonObject.printTo(Serial);
        jsonBuffer.clear();
        preState = postState;
    }

    locallyCalledFun();
}

void servoControl() {
    String recieveData = Serial.readStringUntil('\n');

    String data;

    if (recieveData != "") {
        JsonObject& recieveJson = jsonBuffer.parseObject(recieveData);
        String tmp0 = recieveJson["args0"];
        data = tmp0;
    }

    jsonBuffer.clear();

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

void locallyCalledFun() {
    }
