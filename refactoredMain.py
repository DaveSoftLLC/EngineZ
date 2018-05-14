import pickle
import socket
from math import *

from pygame import *

TCP_IP = '159.203.163.149'
TCP_PORT = 8080
BUFFER_SIZE = 500
mixer.init()
font.init()

otherPlayerDict = {}


class Client:
    def __init__(self, player, TCP_IP, TCP_PORT):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player = player
        self.ip = TCP_IP
        self.port = TCP_PORT

    def get_data(self, running, player):
        global otherPlayerDict
        self.s.connect((self.TCP_IP,self.TCP_PORT))
        while running:
            p = self.player
            binary = pickle.dumps(player)
            self.s.send(binary)
            data = data.decode('utf-8')
            otherPlayerDict = data
        self.s.close()


class GameMode:
    def __init__(self,server=False):
        self.resolution = (1280,800)
        self.players = {}
        if not server:
            self.screen = display.set_mode(self.resolution)
            self.screen.fill((255,255,255))
            self.textFont = font.SysFont("Arial", 25)
            self.screen.blit(transform.smoothscale(image.load('TitleLogo.png'), (1280, 800)), (0, 0))
            self.screen.blit(self.textFont.render('Loading Assets...', True, (0,0,0)), (590, 700))
            display.flip()
            self.music = mixer.music.load("Outcast.wav")
        self.background = image.load('Background/MapFinal.png')
        self.collisionmap = image.load('Background/rocks+hole.png')
        self.running = True

    def draw_screen(self, player):
        try:
            px,py = player.get_pos()
            portion = self.background.subsurface(Rect(px-self.screen.get_width()//2,
                                                 py-self.screen.get_height()//2,
                                                 self.screen.get_width(), self.screen.get_height()))
            self.screen.blit(portion,(0,0))
        except Exception as E:
            print("Error:", E)


class Player:
    def __init__(self, game, name, pos, sprite_files, speed):
        self.name = name
        self.sprites = sprite_files
        self.pos = pos
        self.rotation = 0
        self.state = 0
        self.health = 100
        self.speed = speed
        self.bullets = []
        self.game = game
        self.rect = self.game.screen.blit(self.sprites[self.state], (game.screen.get_width()//2,
                                                                     game.screen.get_height()//2))

    def move(self,direction,map,collisionmap,speed=None):
        if speed is None:
            speed = self.speed
        if direction == 'UP':
            nx,ny = (self.pos[0],self.pos[1] - speed)
            if 0 < ny :
                if collisionmap.get_at((nx,ny))[3] == 0:
                    self.pos = (nx,ny)
        elif direction == 'DOWN':
            nx, ny = (self.pos[0], self.pos[1] + speed)
            if ny < self.game.background.get_height():
                if collisionmap.get_at((nx, ny))[3] == 0:
                    self.pos = (nx,ny)
        elif direction == 'LEFT':
            nx, ny = (self.pos[0] - speed, self.pos[1])
            if 0 < nx:
                if collisionmap.get_at((nx, ny))[3] == 0:
                    self.pos = (nx,ny)
        elif direction == 'RIGHT':
            nx, ny = (self.pos[0] + speed, self.pos[1])
            if nx < self.game.background.get_width():
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
        sprite = transform.rotate(self.sprites[self.state], self.rotation)
        self.rect = self.game.screen.blit(sprite, (640-sprite.get_width()//2, 400-sprite.get_height()//2))
    def get_rect(self):
        return self.rect
    def get_pos(self):
        return self.pos
def renderBullets(Game,player,gunType):
    for b in player.bullets:
        noCol = True
        px,py = player.pos
        nx = b[0][0] + 20*cos(radians(b[1]))
        ny = b[0][1] - 20*sin(radians(b[1]))
        lx,ly = (nx-px + Game.screen.get_width()//2,ny-py + Game.screen.get_height()//2)
        interpolate = [(b[0][0]+i*cos(radians(b[1])),b[0][1]+i*sin(radians(b[1]))) for i in range(10)]
        if 0<lx<Game.screen.get_width() and 0<ly<Game.screen.get_height():
            for cx,cy in interpolate:
                if Game.collisionmap.get_at((int(cx),int(cy)))[3] != 0:
                    noCol = False
            if noCol:
                lb = transform.rotate(gunType.bulletSprite,b[1])
                Game.screen.blit(lb,(lx,ly))
                player.bullets[player.bullets.index(b)] = [(nx,ny),b[1]]
        else:
            del player.bullets[player.bullets.index(b)]
def renderEnemyBullets(Game,userplayer,players,gunType):
    for player in players:
        for b in player.bullets:
            noCol = True
            px, py = player.pos
            nx = b[0][0] + 20 * cos(radians(b[1]))
            ny = b[0][1] - 20 * sin(radians(b[1]))
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
                        userplayer.take_damage(gunType.damage)
            else:
                del player.bullets[player.bullets.index(b)]


class Gun:
    def __init__(self,name,bulletSprite,damage,spread=None):
        self.name = name
        self.bulletSprite = bulletSprite
        self.damage = damage
        self.spread = spread


guns = []
shotgun = Gun('Shotgun', image.load('Weapons/shellBullet.png'), 10, 6)
guns.append(shotgun)
sprites = [image.load('Sprites/sprite1.png'), image.load('Sprites/sprite2.png'), image.load('Sprites/sprite3.png')]
collision = image.load('Background/rocks+hole.png')
g = GameMode()
p = Player(g, 'james', (1200, 1200), sprites, 10)
current_gun = guns[0]
while g.running:
    left_click = False
    for e in event.get():
        if e.type == QUIT:
            g.running = False
        if e.type == MOUSEBUTTONDOWN and e.button == 1:
            left_click = True

    mx, my = mouse.get_pos()
    p.rotation = int(degrees(atan2((g.screen.get_width()//2-mx),(g.screen.get_height()//2-my))))
    px, py = p.get_pos()
    keys = key.get_pressed()
    #UP
    if keys[K_w] and g.screen.get_height()//2<py-p.speed:
        p.move('UP', g.background, g.collisionmap)
    #DOWN
    if keys[K_s] and py+p.speed<g.background.get_height()-g.screen.get_height()//2:
        p.move('DOWN', g.background, g.collisionmap)
    #LEFT
    if keys[K_a] and g.screen.get_width()//2<px-p.speed:
        p.move('LEFT', g.background, g.collisionmap)
    #RIGHT
    if keys[K_d] and px+p.speed<g.background.get_width()-g.screen.get_width()//2:
        p.move('RIGHT', g.background, g.collisionmap)
    if left_click:
        for a in range(1,current_gun.spread):
            spread = p.rotation+90-(3-a)*6
            p.bullets.append([(px+5*cos(radians(spread)), py-5*sin(radians(spread))), spread])
    g.draw_screen(p)
    p.renderPlayer()
    renderBullets(g, p, current_gun)
    draw.rect(g.screen, (0,255,0), p.get_rect(), 5)
    display.flip()
quit()




