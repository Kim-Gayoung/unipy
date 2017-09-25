
import serial
import socket

def dispatch():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    (conn, addr) = s.accept()
    funid = conn.recv(1024)
    if (funid == '1'):
        sendMessage()

def sendMessage():
    data = conn.recv(1024)
    ser = serial.Serial('/dev/ttyACM0')
    ser.write(4)
    ser.write(data)
