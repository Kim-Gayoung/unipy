
import json
import urllib3
_url = 'http://168.131.152.196/common.php'
doorJson = []

def showDoorlist():
    global doorJson
    _field_dict = {}
    _field_dict['_funid'] = 3
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
    _field_dict['_funid'] = 4
    _field_dict['args0'] = deleteInfo
    req = urllib3.PoolManager()
    _isSuccess = req.request('POST', _url, fields=_field_dict).data.decode('utf-8')
    isSuccess = json.loads(_isSuccess)
    if (isSuccess['result'] == True):
        print('Successfully Deleted')
    else:
        print('Failed to Delete')

def main():
    while True:
        print('=====[1] Show doorlist, [2] Delete doorlist=====')
        select = input('Select Command : ')
        if (select == '1'):
            showDoorlist()
        elif (select == '2'):
            deleteDoorInfo()
        else:
            break
