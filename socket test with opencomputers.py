import socket
from pygame import *
import os, threading
TCP_IP = '192.227.178.111'
TCP_PORT = 5005
BUFFER_SIZE = 100  # Normally 1024, but we want fast response
def serverListen(TCP_IP, TCP_PORT):
     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     s.bind((TCP_IP, TCP_PORT))
     s.listen(1)
     while 1:
          lis = ''
          conn, addr = s.accept()
          print('Connection address:', addr)
          data = conn.recv(BUFFER_SIZE)
          if not data: continue
          decoded = data.decode('utf-8')
          
          if decoded == 'quit':
               conn.send('quitting'.encode('utf-8'))
               print('quitting')
               break
     conn.close()
def test(stuff):
     print(stuff)
     return 0
listening = threading.Thread(target=serverListen, args=(TCP_IP,TCP_PORT,)).start()
