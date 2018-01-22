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
        JsonObject& jsonObject = jsonBuffer.createObject();
        jsonObject["_funid"] = 3;
        jsonObject["args0"] = 0;
        jsonObject.printTo(Serial);
        preState = postState;
    }

    if (postState == LOW && preState == HIGH) {
        JsonObject& jsonObject = jsonBuffer.createObject();
        jsonObject["_funid"] = 3;
        jsonObject["args0"] = 1;
        jsonObject.printTo(Serial);
        preState = postState;
    }
}
