
import urllib.request
import urllib3
import json
import serial
_url = 'http://168.131.152.196/common.php'

def dispatch():
    global _ser, _jsonData
    try:
        if (_ser == None):
            raise NameError
    except NameError:
        _ser = serial.Serial('/dev/ttyACM0', 9600)
    jsonStr = _ser.readline().strip().decode('utf-8')
    _jsonData = json.loads(jsonStr)
    funid = _jsonData['_funid']
    if (funid == 3):
        reqSend()
    funid = (- 1)

def reqSend():
    _recieveData = _ser.readline().strip().decode('utf-8')
    global _recieveJsonData
    if (_recieveData != ''):
        _recieveJsonData = json.loads(_recieveData)
    val = _recieveJsonData['args0']
    val = ord(val)
    if (val == 48):
        pic_bin = takeAPhoto()
        _field_dict = {}
        _field_dict['_funid'] = 5
        _field_dict['args0'] = c
        _field_dict['args1'] = pic_bin
        req = urllib3.PoolManager()
        req.request('POST', _url, fields=_field_dict)
    if (val == 49):
        pic_bin = takeAPhoto()
        _field_dict = {}
        _field_dict['_funid'] = 5
        _field_dict['args0'] = o
        _field_dict['args1'] = pic_bin
        req = urllib3.PoolManager()
        req.request('POST', _url, fields=_field_dict)

def takeAPhoto():
    r = urllib.request.urlopen('http://168.131.151.110:8080/stream/snapshot.jpeg')
    pic_bin = r.read()
    return pic_bin
while True:
    _firstCall = dispatch()
