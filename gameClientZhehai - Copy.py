import socket, threading
from pygame import *
from math import*
from glob import*

#TCP_IP = '10.88.214.97'
TCP_IP = '192.227.178.111'
TCP_PORT = 5005
BUFFER_SIZE = 400
running = True
screen = display.set_mode((1280,800))

#Preliminary variables

deg=0
speed=5
state=0

#Chat image
chat=image.load("chat/chat.png")

#Text
font.init()
textB="" #Text that will show for typing, saving
typing=False
agencyfont=font.SysFont("Agency FB",25)

playerList = ["Zhehai",[1300,900],deg,state]
otherPlayers = {}
background = image.load('Background/MapFinal.png')
person = [image.load('Sprites/sprite1.png'),image.load('Sprites/sprite2.png'),image.load('Sprites/sprite3.png')]

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

        elif e.type==MOUSEBUTTONDOWN:
            if e.button==1 and screen.blit(chat,(0,500)).collidepoint(mx,my):
                typing=True
                print("rue")
                textB=""
            elif e.button==1 and typing:
                typing=False

            elif e.button==4 and typing:#Scroll up

            elif e.button==5 and typing:#Scroll down
            
        elif e.type==KEYDOWN:
            if typing:
                if keys[K_BACKSPACE]==1:
                    textB=textB[:-1]
                elif keys[K_RETURN]==1:
                    #Display Text
                    None
                    #Send text via sockets
                else:
                    textB+=e.unicode
    
    mx,my = mouse.get_pos()
    mb = mouse.get_pressed()
    keys = key.get_pressed()


    #Map  
    try:
        portion = background.subsurface(Rect(playerList[1][0]-screen.get_width()//2,playerList[1][1]-screen.get_height()//2,screen.get_width(),screen.get_height()))
        screen.blit(portion,(0,0))
    except:
        print(playerList)
    
    #Movement

    #Sprint
    if keys[K_LSHIFT]:
        speed=10
        state=1
    else:
        speed=5

    #If shooting
    if mb[0]==1:
        state=2
        speed=5
    elif keys[K_LSHIFT]!=True:
        state=0
    #UP
    if keys[K_w] and screen.get_height()//2<playerList[1][1]-speed:
        playerList[1][1] -= speed
    #DOWN
    if keys[K_s] and playerList[1][1]+speed<background.get_height()-screen.get_height()//2:
        playerList[1][1] += speed
    #LEFT
    if keys[K_a] and screen.get_width()//2<playerList[1][0]-speed:
        playerList[1][0] -= speed
    #RIGHT
    if keys[K_d] and playerList[1][0]+speed<background.get_width()-screen.get_width()//2:
        playerList[1][0] += speed

    
    
    #Person moving
    deg=int(degrees(atan2((screen.get_width()//2-mx),(screen.get_height()//2-my))))
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
                rotated = transform.rotate(person[otherPlayers[p][2]],otherPlayers[p][1])
                screen.blit(rotated,(nx,ny))


    #Chat
    
    screen.blit(chat,(0,500))
    if typing==True:
        jsonthing={"Zhehai":"is a cool guy","David":"Python","James":"Cheerios are so amazing trying to make this text rlly long so i can format it"}
        chatBack=Surface((300,300),SRCALPHA)#Alpha surface
        draw.rect(chatBack,(117,117,117,100),(0,0,300,800))
        screen.blit(chatBack,(0,500))
        chaty=550
        for i in jsonthing:
            #i is the name
            if chaty<800:
                chatText=agencyfont.render(i+":",True,((0,0,0)))
                screen.blit(chatText,(0,chaty))
                chaty+=25
            if chaty<800:#character limit is 71
                if len(jsonthing[i])>71:
                    chatText=agencyfont.render(jsonthing[i][:39],True,((0,0,0)))
                    screen.blit(chatText,(0,chaty))
                    chaty+=25
                    if chaty<800:
                        chatText=agencyfont.render(jsonthing[i][39:],True,((0,0,0)))
                        screen.blit(chatText,(0,chaty))
                        chaty+=35
                else:
                    chatText=agencyfont.render(jsonthing[i],True,((0,0,0)))
                    screen.blit(chatText,(0,chaty))
                    chaty+=35
            
            #index is the message
        


    playerList[2]=deg
    playerList[3]=state
    display.flip()
quit()

