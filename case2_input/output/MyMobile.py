
import socket
HOST = '168.131.151.110'
PORT = 8888

def sendControlMessage(data):
    _writer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _writer_tup = (HOST, PORT)
    _writer.connect(_writer_tup)
    _writer.sendall(data.encode('utf-8'))

def main():
    while True:
        print('=====[1] Take Photo, [2] Start/Stop Streaming, [3] Turn Left(Camera), [4] Turn Right(Camera)=====')
        select = input('Select Command : ')
        if (select == '1'):
            pass
        elif (select == '2'):
            pass
        elif (select == '3'):
            sendControlMessage('l')
        elif (select == '4'):
            sendControlMessage('r')
        else:
            break
