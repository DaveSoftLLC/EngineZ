import socket, threading
from pygame import *
TCP_IP = '192.227.178.111'
TCP_PORT = 5005
BUFFER_SIZE = 100
running = True
screen = display.set_mode((800,600))
playerList = ['macbook',(0,0)]
otherPlayers = {}
def getData():
    global BUFFER_SIZE
    global running
    global playerList
    global otherPlayers
    while running:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        s.send(str(playerList).encode('utf-8'))
        try:
            data = eval(s.recv(BUFFER_SIZE).decode('utf-8'))
            otherPlayers[data[0]] = data[1:]
        except:
            pass
        s.close()
threading.Thread(target=getData).start()
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False
    screen.fill(0)
    mx,my = mouse.get_pos()
    m = mouse.get_pressed()
    if m[0] == 1:
        playerList[1] = (mx,my)
    draw.circle(screen, (0,255,0), playerList[1],5)
    for p in otherPlayers:
        draw.circle(screen, (0,255,0), p[1],5)
    display.flip()
quit()
