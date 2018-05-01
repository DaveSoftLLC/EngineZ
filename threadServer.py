import socket
import os, threading
TCP_IP = '192.227.178.111'
TCP_PORT = 5005
BUFFER_SIZE = 200  # Normally 1024, but we want fast response
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
playerDict = {}
running = True
def listen():
     global running
     while running:
          lis = ''
          print("Before looking")
          conn, addr = s.accept()
          print("After looking")
          conn.settimeout(10)
          threading.Thread(target = listenClient,args=(conn,addr)).start()
def listenClient(conn,addr):
     global BUFFER_SIZE
     global playerDict
     global running
     print('thread')
     curPlayer = ''
     while running:
          try:
               data = conn.recv(BUFFER_SIZE)
               if data:
                    decoded = data.decode('utf-8')
                    if decoded == 'quit':
                         conn.send('quitting'.encode('utf-8'))
                         print('quitting')
                         break
                    try:
                         playerList = eval(decoded)
                         playerDict[playerList[0]] = playerList[1:]
                         curPlayer = playerList[0]
                    except:
                         pass
                    conn.send(str(playerDict).encode('utf-8'))
               else:
                    pass
          except:
               del playerDict[curPlayer]
               print('Connection Broken')
               break
     conn.close()
listen()
