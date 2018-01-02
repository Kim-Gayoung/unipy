int doorPin = 2;
int preState = LOW;
int postState = LOW;
void setup() {
    pinMode(doorPin, INPUT);
}
void loop() {
    readDoorSensor();
}
void readDoorSensor() {
    postState = digitalRead(doorPin);
    if (postState == HIGH && preState == LOW) {
        Serial.println(3);
        Serial.println(0);
        preState = postState;
    }
    if (postState == LOW && preState == HIGH) {
        Serial.println(3);
        Serial.println(1);
        preState = postState;
    }
}
