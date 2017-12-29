
import serial
import socket
HOST = ''
PORT = 8888

def dispatch():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(10)
    while 1:
        (conn, addr) = s.accept()
        funid = conn.recv(1024).decode('utf-8')
        if (funid != None):
            break
    if (funid == 2):
        sendMessage()

def sendMessage():
    data = conn.recv(1024)
    ser = serial.Serial('/dev/ttyACM0')
    ser.write(5)
    ser.write(data)
_firstCall = dispatch()
