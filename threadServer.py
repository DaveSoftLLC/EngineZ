<<<<<<< HEAD:socket test with opencomputers.py
import socket,MySQLdb
from pygame import *
import os, threading
mixer.init()
TCP_IP = '192.227.178.111'
TCP_PORT = 5005
BUFFER_SIZE = 100  # Normally 1024, but we want fast response
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
def mysqlStuff(String data):
     db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="engineZ",         # your username
                     passwd="engineZ",  # your password
                     db="engineZ")        # name of the data base

     # you must create a Cursor object. It will let
     #  you execute all the queries you need
     cur = db.cursor()

     # Use all the SQL you like
     cur.execute("SELECT * FROM leaderboard")

     # print all the first cell of all the rows
     for row in cur.fetchall():
         print row[0]

     db.close()
def listen():
     while True:
          lis = ''
          conn, addr = s.accept()
          conn.settimeout(60)
          threading.Thread(target = listenClient,args=(conn,addr)).start()
def listenClient(conn,addr)
     while True:
          try:
               data = conn.recv(BUFFER_SIZE)
               if data:
                    decoded = data.decode('utf-8')
                    if decoded == 'quit':
                         conn.send('quitting'.encode('utf-8'))
                         print('quitting')
                         break
               else:
                    print('No Data')
          except:
               print('Connection Broken')
     conn.close()
listen()
=======
import socket
import os, threading
TCP_IP = '192.227.178.111'
TCP_PORT = 5005
BUFFER_SIZE = 100  # Normally 1024, but we want fast response
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
def listen():#Looking for sockets
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
>>>>>>> 1f7d2d010bb1f143bce0704ea77e67df8c564c61:threadServer.py
