
import serial
import json
import socket
HOST = ''
PORT = 8888

def dispatch():
    global _conn
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(10)
    global _recieveJsonData
    _recieveData = ''
    _cnt = 0
    (_conn, addr) = s.accept()
    while True:
        tmp = _conn.recv(1).decode('utf-8')
        _recieveData += tmp
        if (tmp == '{'):
            _cnt = (_cnt + 1)
        elif (tmp == '}'):
            _cnt = (_cnt - 1)
        if (_cnt == 0):
            break
    _recieveJsonData = json.loads(_recieveData)
    funid = _recieveJsonData['_funid']
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
    _sendFunid = json.dumps(_sendData)
    ser.write(_sendFunid.encode('utf-8'))
    ser.write('\n'.encode('utf-8'))
    _sendData.clear()
    _sendData['args0'] = data
    _jsonData = json.dumps(_sendData)
    ser.write(_jsonData.encode('utf-8'))
    ser.write('\n'.encode('utf-8'))
    ser.close()
_firstCall = dispatch()
