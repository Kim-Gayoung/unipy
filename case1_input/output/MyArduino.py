
_include = 'ArduinoJson.h'
doorPin: int = 2
preState: int = LOW
postState: int = LOW
jsonBuffer: DynamicJsonBuffer

def setup() -> None:
    Serial.begin(9600)
    pinMode(doorPin, INPUT)

def loop() -> None:
    readDoorSensor()

def readDoorSensor() -> None:
    postState = digitalRead(doorPin)
    if ((postState == HIGH) and (preState == LOW)):
        sendFunid: JsonObject = jsonBuffer.createObject()
        sendFunid['_funid'] = 3
        sendFunid.printTo(Serial)
        jsonObject: JsonObject = jsonBuffer.createObject()
        jsonObject['args0'] = 0
        jsonObject.printTo(Serial)
        preState = postState
    if ((postState == LOW) and (preState == HIGH)):
        sendFunid: JsonObject = jsonBuffer.createObject()
        sendFunid['_funid'] = 3
        sendFunid.printTo(Serial)
        jsonObject: JsonObject = jsonBuffer.createObject()
        jsonObject['args0'] = 1
        jsonObject.printTo(Serial)
        preState = postState
