
import serial
import socket
HOST = ''
PORT = 8888

def dispatch():
    global _conn
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(10)
    while 1:
        (_conn, addr) = s.accept()
        funid = int(_conn.recv(1024).decode('utf-8'))
        if (funid != None):
            break
    if (funid == 2):
        sendMessage()

def sendMessage():
    data = _conn.recv(1).decode('utf-8')
    ser = serial.Serial('/dev/ttyACM0', 9600)
    ser.write(str(4).encode('utf-8'))
    ser.write(b'\n')
    ser.write(data.encode('utf-8'))
    ser.write(b'\n')
_firstCall = dispatch()
