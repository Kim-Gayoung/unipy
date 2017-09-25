
_int_doorPin = 2
_int_preState = LOW
_int_postState = LOW

def _void_setup():
    pinMode(doorPin, INPUT)

def _void_loop():
    readDoorSensor()

def _void_readDoorSensor():
    postState = digitalRead(doorPin)
    if ((postState == HIGH) and (preState == LOW)):
        Serial.println(3)
        Serial.println(0)
        preState = postState
    if ((postState == LOW) and (preState == HIGH)):
        Serial.println(3)
        Serial.println(1)
        preState = postState
