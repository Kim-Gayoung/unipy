
_include = 'ArduinoJson.h'
_int_doorPin = 2
_int_preState = LOW
_int_postState = LOW
_DynamicJsonBuffer_jsonBuffer

def _void_setup():
    Serial.begin(9600)
    pinMode(doorPin, INPUT)

def _void_loop():
    readDoorSensor()

def _void_readDoorSensor():
    postState = digitalRead(doorPin)
    if ((postState == HIGH) and (preState == LOW)):
        jsonObject = jsonBuffer.createObject()
        jsonObject['_funid'] = 3
        jsonObject['0'] = 0
        jsonObject.printTo(Serial)
        preState = postState
    if ((postState == LOW) and (preState == HIGH)):
        jsonObject = jsonBuffer.createObject()
        jsonObject['_funid'] = 3
        jsonObject['1'] = 1
        jsonObject.printTo(Serial)
        preState = postState
