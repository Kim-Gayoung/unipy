
import serial
import json
import socket
HOST = ''
PORT = 8888

def dispatch() -> None:
    global _conn
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(10)
    while 1:
        (_conn, addr) = s.accept()
        funid = int(_conn.recv(1024).decode('utf-8'))
        if (funid != None):
            break
    if (funid == 2):
        sendMessage()

def sendMessage():
    _recieveData = ''
    _cnt = 0
    while True:
        tmp = _conn.recv(1).decode('utf-8')
        _recieveData += tmp
        if (tmp == '{'):
            _cnt = (_cnt + 1)
        elif (tmp == '}'):
            _cnt = (_cnt - 1)
        if (_cnt == 0):
            break
    _jsonData = json.loads(_recieveData)
    data = _jsonData['args0']
    global ser
    ser = serial.Serial('/dev/ttyACM0', 9600)
    _sendData = {}
    _sendData['_funid'] = 4
    _sendData['args0'] = data
    _jsonData = json.dumps(_sendData)
    ser.write(_jsonData.encode('utf-8'))
    ser.close()
_firstCall = dispatch()
