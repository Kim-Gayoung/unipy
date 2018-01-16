
_include = 'ArduinoJson.h'
_include = 'Servo.h'
_sensor_decl = _Servo_outerServo
_int_outerPin = 10
_int_pos = 110
_DynamicJsonBuffer_jsonBuffer

def _void_setup():
    Serial.begin(9600)
    outerServo.attach(outerPin)

def _void_loop():
    dispatch()

def _void_dispatch():
    _String_str = ''
    while (Serial.available() > 0):
        str = Serial.readString()
    if (str != ''):
        JsonObject&_jsonObject = jsonBuffer.parseObject(str)
    funid = jsonObject['_funid']
    if (funid == 4):
        servoControl()

def _void_servoControl():
    _String_data = jsonObject['_String_data']
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
