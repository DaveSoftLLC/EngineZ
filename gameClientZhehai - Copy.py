import socket, threading
from pygame import *
#TCP_IP = '10.88.214.97'
TCP_IP = '192.227.178.111'
TCP_PORT = 5005
BUFFER_SIZE = 100
running = True
screen = display.set_mode((800,600))
playerList = [input("Enter your name"),[400,300]]
otherPlayers = {}
background = image.load('OutcastMap.png')
person = image.load("Default Person.png")
def getData():
    global BUFFER_SIZE
    global running
    global playerList
    global otherPlayers
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    while running:
        s.send(str(playerList).encode('utf-8'))
        data = eval(s.recv(BUFFER_SIZE).decode('utf-8'))
        try:
            otherPlayers = data
        except:
            pass
    s.close()

threading.Thread(target=getData).start()
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False

    #Starting Screen




    #Movement and Blitting    
    try:
        portion = background.subsurface(Rect(playerList[1][0]-screen.get_width()//2,playerList[1][1]-screen.get_height()//2,800,600))
        screen.blit(portion,(0,0))
    except:
        print(playerList)
    mx,my = mouse.get_pos()
    m = mouse.get_pressed()
    keysPressed = key.get_pressed()
    #UP
    if keysPressed[K_w] and 300<playerList[1][1]-5:
        playerList[1][1] -= 5
    #DOWN
    if keysPressed[K_s] and playerList[1][1]+5<background.get_height()-300:
        playerList[1][1] += 5
    #LEFT
    if keysPressed[K_a] and 400<playerList[1][0]-5:
        playerList[1][0] -= 5
    #RIGHT
    if keysPressed[K_d] and playerList[1][0]+5<background.get_width()-400:
        playerList[1][0] += 5


        
    screen.blit(person,(365,280))
    for p in otherPlayers:
        if p != playerList[0]:
            draw.circle(screen, (255,255,0), otherPlayers[p][0],5)
    display.flip()
quit()

