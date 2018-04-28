import socket
import os, threading
TCP_IP = '192.227.178.111'
TCP_PORT = 5005
BUFFER_SIZE = 100  # Normally 1024, but we want fast response
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
def listen():
     while True:
          lis = ''
          conn, addr = s.accept()
          conn.settimeout(10)
          threading.Thread(target = listenClient,args=(conn,addr)).start()
def listenClient(conn,addr):
     global BUFFER_SIZE
     while True:
          try:
               data = conn.recv(BUFFER_SIZE)
               if data:
                    decoded = data.decode('utf-8')
                    if decoded == 'quit':
                         conn.send('quitting'.encode('utf-8'))
                         print('quitting')
                         break
                    conn.send(str('Data Received: '+decoded).encode('utf-8'))
               else:
                    pass
          except:
               print('Connection Broken')
               break
     conn.close()
listen()
