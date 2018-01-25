
import urllib.request
import urllib3
import json
import serial
_url = 'http://168.131.152.196/common.php'

def dispatch():
    global _ser, _jsonData
    _ser = serial.Serial('/dev/ttyACM0', 9600)
    jsonStr = ser.readline().strip().decode('utf-8')
    _jsonData = json.loads(jsonStr)
    _funid = _jsonData['_funid']
    if (funid == 3):
        reqSend()

def reqSend():
    _recieveData = ser.readline().strip().decode('utf-8')
    global _jsonData
    _jsonData = json.loads(_recieveData)
    val = _jsonData['args0']
    val = ord(val)
    if (val == 48):
        pic_bin = takeAPhoto()
        _data_dict = {}
        _data_dict['_funid'] = 5
        _data_dict['args0'] = c
        _data_dict['args1'] = pic_bin
        req = urllib3.PoolManager()
        req.request('POST', _url, data=_data_dict)
    if (val == 49):
        pic_bin = takeAPhoto()
        _data_dict = {}
        _data_dict['_funid'] = 5
        _data_dict['args0'] = o
        _data_dict['args1'] = pic_bin
        req = urllib3.PoolManager()
        req.request('POST', _url, data=_data_dict)

def takeAPhoto():
    r = urllib.request.urlopen('http://168.131.151.110:8080/stream/snapshot.jpeg')
    pic_bin = r.read()
    return pic_bin
_firstCall = dispatch()
