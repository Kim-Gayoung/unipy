
import socket
import json
import urllib3
_url = 'http://168.131.152.196/common.php'
doorJson = []
HOST = '168.131.151.110'
PORT = 8888

def showDoorlist():
    global doorJson
    _field_dict = {}
    _field_dict['_funid'] = 4
    req = urllib3.PoolManager()
    _doorJson = req.request('POST', _url, fields=_field_dict).data.decode('utf-8')
    doorJson = json.loads(_doorJson)
    print(doorJson)
    for door in doorJson:
        print(door)

def deleteDoorInfo():
    num = 0
    for door in doorJson:
        print(((str(num) + ' : ') + str(door)))
        num += 1
    selectDel = input('select number : ')
    deleteInfo = doorJson[int(selectDel)].get('d_time')
    _field_dict = {}
    _field_dict['_funid'] = 5
    _field_dict['args0'] = deleteInfo
    req = urllib3.PoolManager()
    _isSuccess = req.request('POST', _url, fields=_field_dict).data.decode('utf-8')
    isSuccess = json.loads(_isSuccess)
    if (isSuccess['result'] == True):
        print('Successfully Deleted')
    else:
        print('Failed to Delete')

def sendControlMessage(data):
    _writer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _sendData = {}
    _writer_tup = (HOST, PORT)
    _writer.connect(_writer_tup)
    _sendData['_funid'] = 9
    _sendFunid = json.dumps(_sendData)
    _writer.sendall(_sendFunid.encode('utf-8'))
    _sendData.clear()
    _sendData['args0'] = data
    _jsonData = json.dumps(_sendData)
    _writer.sendall(_jsonData.encode('utf-8'))

def main():
    while True:
        print('=====[1] doorlist, [2] control camera=====')
        select = input('Select Command: ')
        if (select == '1'):
            print('=====[1] Show doorlist, [2] Delete doorlist=====')
            m_select = input('Select Command : ')
            if (m_select == '1'):
                showDoorlist()
            elif (m_select == '2'):
                deleteDoorInfo()
            else:
                break
        elif (select == '2'):
            print('=====[1] Take Photo, [2] Start/Stop Streaming, [3] Turn Left(Camera), [4] Turn Right(Camera)=====')
            m_select = input('Select Command : ')
            if (m_select == '1'):
                pass
            elif (m_select == '2'):
                pass
            elif (m_select == '3'):
                sendControlMessage('l')
            elif (m_select == '4'):
                sendControlMessage('r')
            else:
                break
