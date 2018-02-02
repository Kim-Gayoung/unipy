
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
    funid: int = 0
    if (Serial.available() > 0):
        str = Serial.readStringUntil(char('\n'))
    if (str != ''):
        jsonObject: JsonObject = jsonBuffer.parseObject(str)
        funid = jsonObject['_funid']
    if (funid == 4):
        servoControl()
    funid = (- 1)

def servoControl() -> None:
    recieveData: String = Serial.readStringUntil(char('\n'))
    data: String
    if (recieveData != ''):
        recieveJson: JsonObject = jsonBuffer.parseObject(recieveData)
        tmp0: String = recieveJson['args0']
        data = tmp0
    jsonBuffer.clear()
    if (data == 'r'):
        pos = (pos - 10)
        data = ''
        if (pos < 0):
            pos = 0
    elif (data == 'l'):
        pos = (pos + 10)
        data = ''
        if (pos > 180):
            pos = 180
    else:
        pass
    outerServo.write(pos)
