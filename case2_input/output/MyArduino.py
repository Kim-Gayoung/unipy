
_include = 'ArduinoJson.h'
_include = 'Servo.h'
_sensor_decl = _Servo_outerServo
outerPin: int = 10
pos: int = 110
jsonBuffer: DynamicJsonBuffer

def setup() -> None:
    Serial.begin(9600)
    outerServo.attach(outerPin)

def loop() -> None:
    dispatch()

def dispatch() -> None:
    str: String = ''
    while (Serial.available() > 0):
        str = Serial.readString()
    if (str != ''):
        jsonObject: JsonObject = jsonBuffer.parseObject(str)
    funid = jsonObject['_funid']
    if (funid == 4):
        servoControl()

def servoControl() -> None:
    recieveData: String = ''
    while (Serial.available() > 0):
        recieveData = Serial.readString()
    if (recieveData != ''):
        jsonObject: JsonObject = jsonBuffer.createObject()
    data: String = jsonObject['args0']
    if (data == 'r'):
        pos = (pos - 10)
        data = 0
        if (pos < 0):
            pos = 0
    elif (data == 'l'):
        pos = (pos + 10)
        data = 0
        if (pos > 180):
            pos = 180
    else:
        pass
    outerServo.write(pos)
