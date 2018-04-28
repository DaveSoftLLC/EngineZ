import socket
from pygame import *
TCP_IP = '192.227.178.111'
TCP_PORT = 5005
BUFFER_SIZE = 100
running = True
screen = display.set_mode((800,600))
playerList = []
otherPlayers = {}
def getData():
    global BUFFER_SIZE
    global running
    global playerList
    global otherPlayers
    while running:
        MESSAGE = input('Enter text')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        s.send(MESSAGE.encode('utf-8'))
        data = s.recv(BUFFER_SIZE)
        s.close()
        if MESSAGE == 'QUIT':
            break
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False
    
