
_include = 'Servo.h'
_sensor_decl = _Servo_outerServo
_int_outerPin = 10
_int_pos = 110
_int_receivedAscii = 0
_char_data = ''

def _void_dispatch():
    _char_funid = ''
    if (Serial.available() > 0):
        funid = Serial.read()
    if (funid == 5):
        servoControl()

def _void_setup():
    Serial.begin(9600)
    outerServo.attach(outerPin)

def _void_loop():
    servoControl(data)

def _void_servoControl():
    data = Serial.read()
    if (receivedAscii == 114):
        pos = (pos - 10)
        receivedAscii = 0
        if (pos < 0):
            pos = 0
    elif (receivedAscii == 108):
        pos = (pos + 10)
        receivedAscii = 0
        if (pos > 180):
            pos = 180
    else:
        pass
    outerServo.write(pos)
_firstCall = dispatch()
