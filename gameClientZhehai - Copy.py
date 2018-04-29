import socket, threading
from pygame import *
from math import*
from glob import*

#TCP_IP = '10.88.214.97'
TCP_IP = '192.227.178.111'
TCP_PORT = 5005
BUFFER_SIZE = 100
running = True
screen = display.set_mode((800,600))

#Preliminary variables

deg=0
speed=5
state=0


playerList = [input("Enter your name"),[400,300],deg,state]
otherPlayers = []
background = image.load('OutcastMap.png')
person = [image.load('Sprites/sprite1.png'),image.load('Sprites/sprite2.png'),image.load('Sprites/sprite3.png')]
print(person)
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




    #Movement and Blitting    
    try:
        portion = background.subsurface(Rect(playerList[1][0]-screen.get_width()//2,playerList[1][1]-screen.get_height()//2,800,600))
        screen.blit(portion,(0,0))
    except:
        print(playerList)
    mx,my = mouse.get_pos()
    mb = mouse.get_pressed()
    keysPressed = key.get_pressed()

    if keysPressed[K_LSHIFT]:
        speed=10
        state=1
    else:
        speed=5

    if mb[0]==1:
        state=2
        speed=5
    elif keysPressed[K_LSHIFT]!=True:
        state=0
    #UP
    if keysPressed[K_w] and 300<playerList[1][1]-speed:
        playerList[1][1] -= speed
    #DOWN
    if keysPressed[K_s] and playerList[1][1]+speed<background.get_height()-screen.get_height()//2:
        playerList[1][1] += speed
    #LEFT
    if keysPressed[K_a] and 400<playerList[1][0]-speed:
        playerList[1][0] -= speed
    #RIGHT
    if keysPressed[K_d] and playerList[1][0]+speed<background.get_width()-screen.get_width()//2:
        playerList[1][0] += speed

    
    
    #Person moving
    deg=degrees(atan2((screen.get_width()//2-mx),(screen.get_height()//2-my)))
    rotated = transform.rotate(person[state],deg)
    screen.blit(rotated,(screen.get_width()//2-rotated.get_width()//2,screen.get_height()//2-rotated.get_height()//2))#Around 400,300 but just modified for rotation
    
    #draw.circle(screen, (255,255,0), playerList[1],5)

    #Draws Other Players 
    for p in otherPlayers:
        if p != playerList[0]: #Make sure it's not your own
            px,py = playerList[1]
            nx,ny = otherPlayers[p][0]
            if px-screen.get_width()//2<nx<px+screen.get_width() and py-screen.get_height()//2<ny<py+screen.get_height()//2: #If the enemy is within your screen
                nx = nx-px +screen.get_width()//2 #gets the enemy position in your screen
                ny = ny-py +screen.get_height()//2
                deg=degrees(atan2((screen.get_width()//2-nx),(screen.get_height()//2-ny)))
                rotated = transform.rotate(otherPlayers[p][3],otherPlayers[p][2])
                screen.blit(rotated,(screen.get_width()//2-rotated.get_width()//2,screen.get_height()//2-rotated.get_height()//2))
    display.flip()
quit()

