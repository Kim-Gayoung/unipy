
import json
import os
import pymysql
import sys

def dispatch():
    funid = int(sys.argv[1])
    if (funid == 3):
        selectDoorlist()
    if (funid == 4):
        deleteDoorlist()

def selectDoorlist():
    conn = pymysql.connect(host='localhost', user='capstone', password='capstone17', db='capstone', charset='utf8')
    result = []
    try:
        with conn.cursor() as cursor:
            sql = 'select d_time, d_openclose from doorlist order by d_time'
            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            tmp = []
            for row in rows:
                if (type(row[0]).__name__ == 'datetime'):
                    tmp.append([str(row[0]), row[1]])
            rows = tmp
            del tmp
            for row in rows:
                row = dict(zip(columns, row))
                result.append(row)
        conn.close()
        print(json.dumps(result))
    except:
        conn.close()
        print()

def deleteDoorlist():
    deleteInfo = sys.argv[2]
    conn = pymysql.connect(host='localhost', user='capstone', password='capstone17', db='capstone', charset='utf8')
    try:
        with conn.cursor() as cursor:
            sql = 'select d_pic_loc from doorlist where d_time = %s'
            cursor.execute(sql, deleteInfo)
            row = cursor.fetchone()
            pic_loc = ('D:\\APM\\Apache24\\htdocs\\sechome\\door\\' + row[0])
        with open(pic_loc, 'r') as f:
            f.close()
            os.unlink(pic_loc)
        with conn.cursor() as cursor:
            sql = 'delete from doorlist where d_time = %s'
            cursor.execute(sql, deleteInfo)
            conn.commit()
        conn.close()
        print(json.dumps({'result': True}))
    except:
        conn.close()
        print(json.dumps({'result': False}))
_firstCall = dispatch()
