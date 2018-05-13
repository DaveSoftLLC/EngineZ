import pickle
import socket
from math import *

from pygame import *

TCP_IP = '159.203.163.149'
TCP_PORT = 8080
BUFFER_SIZE = 500
mixer.init()
font.init()

<<<<<<< HEAD

#TO DO:

#1. Put in all the variables we had in MAIN.py:
    #Speed - Shift runs faster, shooting slows person down
    #Rotation -
    #deg=int(degrees(atan2((screen.get_width()//2-mx),(screen.get_height()//2-my))))
    #rotated = transform.rotate(person[state],deg)
    #playerSprite = screen.blit(rotated,(screen.get_width()//2-rotated.get_width()//2,screen.get_height()//2-rotated.get_height()//2))
    #playerList - name, bullets, rotation, state(running shooting)

#2. SERVER CLIENT CONNECTION
    



=======
otherPlayerDict = {}

class Client:
    def __init__(self,player,TCP_IP,TCP_PORT):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player = player
        self.ip = TCP_IP
        self.port = TCP_PORT

    def getData(self,running):
        global otherPlayerDict
        self.s.connect((self.TCP_IP,self.TCP_PORT))
        while running:
            p = self.player
            playerList = [p.name,p.pos,p.rotation,p.state,p.health,p.bullets,p.speed]
            binary = pickle.dumps(playerList)
            self.s.send(binary)
            data = pickle.loads(self.s.recv(500))
            otherPlayerDict = data
        self.s.close()
>>>>>>> 4998de398eabec6b43b1d930f3c8e0d9adb4828a





class GameMode:
    def __init__(self,server=False):
        self.resolution = (1280,800)
        self.players = {}
        if not server:
            self.music = mixer.music.load("Outcast.wav")
            self.textFont = font.SysFont("Arial",25)
            self.screen = display.set_mode(self.resolution)
        self.background = image.load('Background/MapFinal.png')
        self.collisionmap = image.load('Background/rocks+hole.png')
<<<<<<< HEAD
        self.screen = display.set_mode(self.resolution)
        #Weapons:
        self.shotgun = image.load("Weapons/shotgun.png")
        self.slot = 0 #axe
        self.inventory = {1:"",2:"",3:"",4:"",5:"",6:""}
=======
>>>>>>> 4998de398eabec6b43b1d930f3c8e0d9adb4828a
        self.running = True


    def gameLoop(self):
        mx,my = mouse.get_pos()
        for e in event.get():
            if e.type == QUIT:
                self.running = False
            if e.type==MOUSEBUTTONDOWN:
                None
            mb = mouse.get_pressed()
            self.screen.blit(self.back,(0,0))
            self.checkstate(self.state)
            if mb[0]==1:
                None 
            display.flip()
    def drawScreen(self,player):
        try:
            px,py = player.get_pos()
            portion = self.background.subsurface(Rect(px-self.screen.get_width()//2,
                                                 py-self.screen.get_height()//2,
                                                 self.screen.get_width(),self.screen.get_height()))
            self.screen.blit(portion,(0,0))
        except:
            print("Error")

class Player:
    def __init__(self,game,name,pos,spritefiles,speed):
        self.name = name
        self.sprites = spritefiles
        self.pos = pos
        self.rotation = 0
        self.state = 0
        self.health = 100
        self.speed = speed
        self.bullets = []
        self.game = game
        self.rect = self.game.screen.blit(self.sprites[self.state],(game.screen.get_width()//2,game.screen.get_height()//2))
    def move(self,direction,map,collisionmap,speed=None):
        if speed is None:
            speed = self.speed
        if direction == 'UP':
            nx,ny = (self.pos[0],self.pos[1] - speed < map.get_height())
            if 0<nx :
                if collisionmap.get_at((nx,ny))[3] == 0:
                    self.pos = (nx,ny)
        elif direction == 'DOWN':
            nx, ny = (self.pos[0], self.pos[1] + speed < map.get_height())
            if 0 < nx:
                if collisionmap.get_at((nx, ny))[3] == 0:
                    self.pos = (nx,ny)
        elif direction == 'LEFT':
            nx, ny = (self.pos[0] - speed < map.get_height(), self.pos[1])
            if 0 < nx:
                if collisionmap.get_at((nx, ny))[3] == 0:
                    self.pos = (nx,ny)
        elif direction == 'UP':
            nx, ny = (self.pos[0] + speed < map.get_height(), self.pos[1])
            if 0 < nx:
                if collisionmap.get_at((nx, ny))[3] == 0:
                    self.pos = (nx,ny)
    def takeDamage(self,amount):
        if self.health-amount > 0:
            self.health -= amount
        else:
            self.die()
    def die(self):
        print("dead")
        pass
    def fire(self):
        px,py = self.pos
        for a in range(1,6):
            angle = self.rotation+90-(3-a)*6
            self.bullets.append([(px+5*cos(radians(angle)),py-5*sin(radians(angle))),angle])
    def renderPlayer(self):
        self.rect = self.game.screen.blit(self.sprites[self.state],self.pos)
def renderBullets(Game,player,gunType):
    for b in player.bullets:
        noCol = True
        px,py = player.pos
        nx = b[0][0] + 10*cos(radians(b[1]))
        ny = b[0][1] - 10*sin(radians(b[1]))
        lx,ly = (nx-px + Game.screen.get_width()//2,ny-py + Game.screen.get_height()//2)
        interpolate = [(b[0][0]+i*cos(radians(b[1])),b[0][1]+i*sin(radians(b[1]))) for i in range(10)]
        if 0<lx<Game.screen.get_width() and 0<ly<Game.screen.get_height():
            for cx,cy in interpolate:
                if Game.collisionmap.get_at((int(cx),int(cy)))[3] != 0:
                    noCol = False
            if noCol:
                lb = transform.rotate(gunType.bulletsprite,b[1])
                Game.screen.blit(lb,(lx,ly))
                player.bullets[player.bullets.index(b)] = [(nx,ny),b[1]]
        else:
            del player.bullets[player.bullets.index(b)]
def renderEnemyBullets(Game,userplayer,players,gunType):
    for player in players:
        for b in player.bullets:
            noCol = True
            px, py = player.pos
            nx = b[0][0] + 10 * cos(radians(b[1]))
            ny = b[0][1] - 10 * sin(radians(b[1]))
            lx, ly = (nx - px + Game.screen.get_width() // 2, ny - py + Game.screen.get_height() // 2)
            interpolate = [(b[0][0] + i * cos(radians(b[1])), b[0][1] + i * sin(radians(b[1]))) for i in range(10)]
            if 0 < lx < Game.screen.get_width() and 0 < ly < Game.screen.get_height():
                for cx, cy in interpolate:
                    if Game.collisionmap.get_at((int(cx), int(cy)))[3] != 0:
                        noCol = False
                if noCol:
                    lb = transform.rotate(gunType.bulletsprite, b[1])
                    shot = Game.screen.blit(lb, (lx, ly))
                    player.bullets[player.bullets.index(b)] = [(nx, ny), b[1]]
                    if shot.colliderect(userplayer.rect):
                        userplayer.takeDamage(gunType.damage)
            else:
                del player.bullets[player.bullets.index(b)]

<<<<<<< HEAD
class gunType:
    def bulletsprite(self,name):
        
        if name == "shotgun":
            return shotgun

    def damage(self,slot):
        None
=======
class Gun:
    def __init__(self,name,bulletSprite,damage):
        self.name = name
        self.bulletSprite = bulletSprite
        self.damage = damage
>>>>>>> 4998de398eabec6b43b1d930f3c8e0d9adb4828a






