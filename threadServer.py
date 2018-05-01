import socket
import os, threading
TCP_IP = '159.203.163.149'
TCP_PORT = 8080
BUFFER_SIZE = 500  # Normally 1024, but we want fast response
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
playerDict = {}
def listen():
     while True:
          lis = ''
          print("Before looking")
          conn, addr = s.accept()
          print("After looking")
          conn.settimeout(10)
          threading.Thread(target = listenClient,args=(conn,addr)).start()
def listenClient(conn,addr):
     global BUFFER_SIZE
     global playerDict
     print('thread')
     curPlayer = ''
     while True:
          try:
               data = conn.recv(BUFFER_SIZE)
               if data:
                    try:
                         decoded = data.decode('utf-8')
                         playerList = eval(decoded)
                         playerDict[playerList[0]] = playerList[1:]
                         curPlayer = playerList[0]
                         conn.send(str(playerDict).encode('utf-8'))
                    except:
                         pass
               else:
                    pass
          except Exception as E:
               del playerDict[curPlayer]
               print('Connection Broken:',E)
               break
     conn.close()
listen()
