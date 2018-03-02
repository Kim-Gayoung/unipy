
import urllib.request
import urllib3
import serial
import json
import socket
import threading
HOST = ''
PORT = 8888
_url = 'http://168.131.152.196/common.php'

def dispatch_Socket():
    global _conn
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    while True:
        (_conn, addr) = s.accept()
        global _recieveJsonData
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
        if (_recieveData == ''):
            continue
        _recieveJsonData = json.loads(_recieveData)
        funid = _recieveJsonData['_funid']
        if (funid == 9):
            sendMessage()
        funid = (- 1)

def dispatch_Serial():
    global _ser, _jsonData
    _ser = serial.Serial('/dev/ttyACM0', 9600)
    while True:
        jsonStr = _ser.readline().strip().decode('utf-8')
        if (jsonStr == ''):
            continue
        _jsonData = json.loads(jsonStr)
        funid = _jsonData['_funid']
        if (funid == 10):
            reqSend()
        funid = (- 1)

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
    global _jsonData
    if (_recieveData != ''):
        _jsonData = json.loads(_recieveData)
    else:
        _jsonData = ''
    if (_jsonData != ''):
        data = _jsonData['args0']
    global ser
    ser = serial.Serial('/dev/ttyACM0', 9600)
    _sendData = {}
    _sendData['_funid'] = 14
    _sendFunid = json.dumps(_sendData)
    ser.write(_sendFunid.encode('utf-8'))
    ser.write('\n'.encode('utf-8'))
    _sendData.clear()
    _sendData['args0'] = data
    _jsonData = json.dumps(_sendData)
    ser.write(_jsonData.encode('utf-8'))
    ser.write('\n'.encode('utf-8'))
    ser.close()

def reqSend():
    _recieveData = _ser.readline().strip().decode('utf-8')
    global _recieveJsonData
    if (_recieveData != ''):
        _recieveJsonData = json.loads(_recieveData)
    else:
        _recieveJsonData = ''
    if (_recieveJsonData != ''):
        val = _recieveJsonData['args0']
    val = ord(val)
    if (val == 48):
        pic_bin = takeAPhoto()
        _field_dict = {}
        _field_dict['_funid'] = 6
        _field_dict['args0'] = c
        _field_dict['args1'] = pic_bin
        req = urllib3.PoolManager()
        req.request('POST', _url, fields=_field_dict)
    if (val == 49):
        pic_bin = takeAPhoto()
        _field_dict = {}
        _field_dict['_funid'] = 6
        _field_dict['args0'] = o
        _field_dict['args1'] = pic_bin
        req = urllib3.PoolManager()
        req.request('POST', _url, fields=_field_dict)

def takeAPhoto():
    r = urllib.request.urlopen('http://168.131.151.110:8080/stream/snapshot.jpeg')
    pic_bin = r.read()
    return pic_bin
thread0 = threading.Thread(target=dispatch_Socket, args=())
thread1 = threading.Thread(target=dispatch_Serial, args=())
thread0.start()
thread1.start()
thread0.join()
thread1.join()
