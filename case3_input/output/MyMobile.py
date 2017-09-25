
import urllib3
_url = 'http://168.131.152.196/common.php'

def doorlist():
    req = urllib3.PoolManager()
    doorJson = req.request('POST', _url, fields={'_funid': '2'})

def deleteDoorInfo(deleteInfo):
    req = urllib3.PoolManager()
    isCommit = req.request('POST', _url, fields={'_funid': '3', 'MOBILE_CLOUD_ARGS_0': 'deleteInfo'})
