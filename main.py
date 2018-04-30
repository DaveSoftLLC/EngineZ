import socket, threading
from pygame import *
from math import*
from glob import*
import copy
import requests
import json
#TCP_IP = '10.88.214.97'
TCP_IP = '192.227.178.111'
TCP_PORT = 5005
BUFFER_SIZE = 500
running = True
screen = display.set_mode((1280,800))

#Preliminary variables
mixer.init()
currentMusic=mixer.music.load("Outcast.wav")
mixer.music.set_volume(0.5)
mixer.music.play()
deg=0
speed=5
state=0
chatf=550
#Chat image
chat=image.load("chat/chat.png")
jsonthing={"User":["Welcome!"],"Message":["Type anything to chat"]}
lastID = 0
scrolllimit=[jsonthing["User"][0],jsonthing["Message"][0]]
#Text
font.init()
textB="" #Text that will show for typing, saving
typing=False
agencyfont=font.SysFont("Agency FB",25)
health = 100
bullets = []
playerList = ["Demo",[1300,900],deg,state,health,bullets]
otherPlayers = {}
background = image.load('Background/MapFinal.png')
person = [image.load('Sprites/sprite1.png'),image.load('Sprites/sprite2.png'),image.load('Sprites/sprite3.png')]
lbullet = image.load('Weapons/shellBullet.png')
otherBullets = []
def getData():
    global BUFFER_SIZE
    global running
    global playerList
    global otherPlayers
    global bullets
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    while running:
        playerList
        s.send(str(playerList).encode('utf-8'))
        data = eval(s.recv(BUFFER_SIZE).decode('utf-8'))
        try:
            otherPlayers = data
        except:
            pass
    s.close()
    
def getChat():
    global jsonthing
    global lastID
    global running
    while running:
        headers = {
            'Content-Type': "text/plain",
            'Cache-Control': "nocache"
        }
        jsonstring = '{"command" : "getChat"}'
        r = requests.request("POST","http://s01.jamesxu.ca:5006",data=jsonstring,headers=headers)
        recvJSON = r.text
        
        dicJSON = json.loads(r.text)
        remoteMessID = dicJSON['messID']
        
        if(remoteMessID > lastID):
            remoteUser = dicJSON['user']
            remoteMessage = dicJSON['message']
            jsonthing['User'].append(remoteUser)
            jsonthing['Message'].append(remoteMessage)
            lastID = remoteMessID
    
threading.Thread(target=getData).start()
threading.Thread(target=getChat).start()

while running:
    fire = False
    for e in event.get():
        if e.type == QUIT:
            running = False

        elif e.type==MOUSEBUTTONDOWN:
            if e.button == 1:
                #fire = True
                None
            if e.button==1 and screen.blit(chat,(0,500)).collidepoint(mx,my):
                typing=True
                
                textB=""
            elif e.button==1 and typing:
                typing=False

            elif e.button==4 and typing and chatf+10<800:
                chatf+=10
                """
                chat1=[]
                chat1.append(jsonthing["User"][-1])
                for i in range(len(jsonthing["User"])-1):
                    chat1.append(jsonthing["User"][i])
                jsonthing["User"]=copy.deepcopy(chat1)

                chat1=[]
                chat1.append(jsonthing["Message"][-1])
                for i in range(len(jsonthing["Message"])-1):
                    chat1.append(jsonthing["Message"][i])
                jsonthing["Message"]=copy.deepcopy(chat1)
                """
            elif e.button==5 and typing and chatf-10>100:#Scroll down: move first index to last
                """
                chat1=[]
                for i in range(1,len(jsonthing["User"])):
                    chat1.append(jsonthing["User"][i])
                chat1.append(jsonthing["User"][0])
                jsonthing["User"]=copy.deepcopy(chat1)

                chat1=[]
                for i in range(1,len(jsonthing["Message"])):
                    chat1.append(jsonthing["Message"][i])
                chat1.append(jsonthing["Message"][0])
                print(chat1)
                jsonthing["Message"]=copy.deepcopy(chat1)
                """
                chatf-=10
        elif e.type==KEYDOWN:
            if typing:
                keys=key.get_pressed()
                if keys[K_BACKSPACE]==1:
                    textB=textB[:-1]
                elif keys[K_RETURN]==1:
                    #Display Text
                    if textB!="":
                        
                        jsonthing["User"].append(playerList[0])
                        jsonthing["Message"].append(textB)
                        headers = {
                            'Content-Type': "text/plain",
                            'Cache-Control': "nocache"
                        }
                        jsonstring = '{"command" : "putChat","user" : "' + playerList[0] + '","message" : "' + textB +'"}'
                        r = requests.request("POST","http://s01.jamesxu.ca:5006",data=jsonstring,headers=headers)
                        textB=""
                        lastID += 1
                        #Send text via socketss
                        
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
    playerSprite = screen.blit(rotated,(screen.get_width()//2-rotated.get_width()//2,screen.get_height()//2-rotated.get_height()//2))#Around 400,300 but just modified for rotation
    
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
            otherBullets += otherPlayers[p][4]

    #Chat
    
    screen.blit(chat,(0,500))
    screen.set_clip(Rect(0,500,300,300))
    if typing==True:
        chatBack=Surface((300,300),SRCALPHA)#Alpha surface
        draw.rect(chatBack,(117,117,117,100),(0,0,300,800))
        screen.blit(chatBack,(0,500))
        
        chatType=agencyfont.render(textB,True,((0,0,0)))
        screen.blit(chatType,(0,750))
        chaty=chatf
        chatHeight = 0
        for i in range(len(jsonthing["Message"])):
            #i is the name
            if chaty<700:
                chatText=agencyfont.render(jsonthing["User"][i]+":",True,((0,0,0)))
                screen.blit(chatText,(0,chaty))
                chaty+=25
                chatHeight += chatText.get_height()
            if chaty<700:#character limit is 71
                if len(jsonthing["Message"][i])>71:
                    chatText=agencyfont.render(jsonthing["Message"][i][:39],True,((0,0,0)))
                    screen.blit(chatText,(0,chaty))
                    chaty+=25
                    
                    if chaty<700:
                        chatText=agencyfont.render(jsonthing["Message"][i][39:],True,((0,0,0)))
                        screen.blit(chatText,(0,chaty))
                        chaty+=35
                else:
                    chatText=agencyfont.render(jsonthing["Message"][i],True,((0,0,0)))
                    screen.blit(chatText,(0,chaty))
                    chaty+=35
            
            #index is the messag=2
    screen.set_clip(None)
    
    #HealthBar
    draw.rect(screen,(255,0,0),(10,10,300,30),0)
    draw.rect(screen,(0,255,0),(10,10,health*3,30),0)
    #Shooting - 
    if fire:
        for a in range(1,6):
            bullets.append([(screen.get_width()//2,screen.get_height()//2),deg+90-(3-a)*15])
    for b in bullets:
        if 0<b[0][0]+5*cos(b[1])<screen.get_width() and 0<b[0][1]-5*sin(b[1])<screen.get_height():
            ox,oy = (int(b[0][0]),int(b[0][1]))
            lb = transform.rotate(lbullet,deg)
            nx,ny = (int(b[0][0]+5*cos(radians(b[1]))),int(b[0][1]-5*sin(radians(b[1]))))
            shot = screen.blit(lb,(nx,ny))
            if shot.colliderect(playerSprite):
                health -= 10
            bullets[bullets.index(b)] = [(nx,ny),b[1]]
        else:
            del bullets[bullets.index(b)]
    for b in otherBullets:
        if 0<b[0][0]+5*cos(b[1])<screen.get_width() and 0<b[0][1]-5*sin(b[1])<screen.get_height():
            ox,oy = (int(b[0][0]),int(b[0][1]))
            lb = transform.rotate(lbullet,deg)
            nx,ny = (int(b[0][0]+5*cos(radians(b[1]))),int(b[0][1]-5*sin(radians(b[1]))))
            shot = screen.blit(lb,(nx,ny))
            if shot.colliderect(playerSprite):
                health -= 10
            otherBullets[otherBullets.index(b)] = [(nx,ny),b[1]]
        else:
            del otherBullets[otherBullets.index(b)]
    playerList[2]=deg
    playerList[3]=state
    display.flip()
quit()

