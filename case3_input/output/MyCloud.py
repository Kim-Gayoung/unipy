
import pymysql
import cgi

def dispatch():
    funid = cgi.FieldStorage()['_funid'].value
    if (funid == '2'):
        selectDoorlist()

def selectDoorlist():
    sql = 'select * from doorlist order by d_time'

def deleteDoorlist():
    deleteInfo = cgi.FieldStorage()['MOBILE_CLOUD_ARGS_0'].value
    sql = (("delete from doorlist where d_time = '" + deleteInfo) + "'")
