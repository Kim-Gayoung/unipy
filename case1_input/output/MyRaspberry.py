
import urllib.request
import urllib3
import serial
_url = 'http://168.131.152.196/common.php'

def dispatch():
    ser = serial.Serial('/dev/ttyACM0')
    funid = ser.read(1)
    if (funid == 3):
        reqSend()

def reqSend():
    val = ser.read(1)
    if (val == 48):
        pic_bin = takeAPhoto()
        req = urllib3.PoolManager()
        req.request('POST', '_url', data={'_funid': '5', 'GATEWAY_CLOUD_ARGS_0': 'c', 'GATEWAY_CLOUD_ARGS_1': 'pic_bin'})
    if (val == 49):
        pic_bin = takeAPhoto()
        req = urllib3.PoolManager()
        req.request('POST', '_url', data={'_funid': '5', 'GATEWAY_CLOUD_ARGS_0': 'o', 'GATEWAY_CLOUD_ARGS_1': 'pic_bin'})

def takeAPhoto():
    pic_bin = r.read()
    return pic_bin
_firstCall = dispatch()
