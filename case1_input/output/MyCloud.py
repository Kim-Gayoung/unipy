
import cgi

def dispatch():
    funid = cgi.FieldStorage()['_funid'].value
    if (funid == '4'):
        recordDoorState()

def recordDoorState():
    openclose = cgi.FieldStorage()['MOBILE_CLOUD_ARGS_0'].value
    pic_bin = cgi.FieldStorage()['MOBILE_CLOUD_ARGS_1'].value
    d_pic_loc = save_picture(pic_bin)
