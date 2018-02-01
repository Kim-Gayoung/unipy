
import pymysql
import os
import sys

def dispatch():
    funid = int(sys.argv[1])
    if (funid == 5):
        recordDoorState()
    funid = (- 1)

def recordDoorState():
    openclose = sys.argv[2]
    pic_bin = sys.argv[3]
    d_pic_loc = save_picture(pic_bin)
    isSuccess = save_doorState(openclose, d_pic_loc)

def save_picture(pic_bin):
    num = 1
    pic_loc = (('D:\\APM\\Apache24\\htdocs\\sechome\\door\\door' + str(num)) + '.jpg')
    while os.path.isfile(pic_loc):
        num = (num + 1)
        pic_loc = (('D:\\APM\\Apache24\\htdocs\\sechome\\door\\door' + str(num)) + '.jpg')
    return pic_loc

def save_doorState(openclose, d_pic_loc):
    conn = pymysql.connect(host='localhost', user='capstone', password='capstone17', db='capstone', charset='utf8')
    try:
        with conn.cursor() as cursor:
            sql = 'insert into doorlist(d_openclose, d_pic_loc) values(%s, %s)'
            cursor.execute(sql, (openclose, d_pic_loc))
            conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False
while True:
    _firstCall = dispatch()
