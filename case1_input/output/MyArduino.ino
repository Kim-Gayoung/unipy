#include <ArduinoJson.h>

int doorPin = 2;
int preState = LOW;
int postState = LOW;
DynamicJsonBuffer jsonBuffer;

void setup() {
    Serial.begin(9600);

    pinMode(doorPin, INPUT);
}

void loop() {
    readDoorSensor();
}

void readDoorSensor() {
    postState = digitalRead(doorPin);

    if (postState == HIGH && preState == LOW) {
        JsonObject& sendFunid = jsonBuffer.createObject();
        sendFunid["_funid"] = 2;
        sendFunid.printTo(Serial);
        JsonObject& jsonObject = jsonBuffer.createObject();
        jsonObject["args0"] = 0;
        jsonObject.printTo(Serial);
        jsonBuffer.clear();
        preState = postState;
    }

    if (postState == LOW && preState == HIGH) {
        JsonObject& sendFunid = jsonBuffer.createObject();
        sendFunid["_funid"] = 2;
        sendFunid.printTo(Serial);
        JsonObject& jsonObject = jsonBuffer.createObject();
        jsonObject["args0"] = 1;
        jsonObject.printTo(Serial);
        jsonBuffer.clear();
        preState = postState;
    }
}
