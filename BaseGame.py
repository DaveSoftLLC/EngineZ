import pickle
import socket
from math import *

from pygame import *

TCP_IP = '159.203.163.149'
TCP_PORT = 8080
BUFFER_SIZE = 5000


class Client:
    def __init__(self, player, game, TCP_IP, TCP_PORT, sprites):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player = player
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.game = game
        self.other_player_dict = dict()
        self.sprites = sprites

    def update_player(self, player):
        self.player = player

    def get_data(self):
        global otherPlayerDict
        self.s.connect((self.TCP_IP,self.TCP_PORT))
        print('beginning transfer')
        while self.game.running:
            p = self.player
            binary = pickle.dumps(p)
            self.s.send(binary)
            data = self.s.recv(BUFFER_SIZE)
            data = pickle.loads(data)
            self.other_player_dict = data
            p.health = self.other_player_dict[p.name].health
        self.s.close()

    def render_other_players(self):
        p = self.player
        g = self.game
        for o in self.other_player_dict.values():
            if o.name != p.name:
                px, py = p.get_pos()
                ox, oy = o.get_pos()
                if px - g.screen.get_width() // 2 < ox < px + g.screen.get_width() and py - g.screen.get_height() // 2 < oy < py + g.screen.get_height() // 2:
                    nx = ox - px + g.screen.get_width() // 2  # gets the enemy position in your screen
                    ny = oy - py + g.screen.get_height() // 2
                    other_sprite = transform.rotate(self.sprites[o.state][o.gif_counter // 10], o.rotation + 90)
                    other_sprite = transform.smoothscale(other_sprite, (
                    other_sprite.get_width() // 3, other_sprite.get_height() // 3))
                    g.screen.blit(other_sprite, (nx, ny))

    def render_enemy_bullets(self, gun):
        p = self.player
        g = self.game
        for o in otherPlayerDict:
            if o.name != p.name:
                px, py = p.get_pos()
                for b in o.bullets:
                    bx = b[0][0] + 20 * cos(radians(b[1]))
                    by = b[0][1] - 20 * sin(radians(b[1]))
                    lx, ly = (bx - px + g.screen.get_width() // 2, by - py + g.screen.get_height() // 2)
                    lb = transform.rotate(gun.bulletSprite, b[1])
                    g.screen.blit(lb)


class GameMode:
    def __init__(self,server=False):
        self.resolution = (1280,800)
        self.players = {}
        if not server:
            mixer.init()
            font.init()
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
    def __init__(self, game, name, pos, speed):
        self.name = name
        self.pos = pos
        self.rotation = 90
        self.state = 0
        self.health = 100
        self.speed = speed
        self.bullets = []
        self.rect = None
        self.gif_counter = 0

    def move(self, direction, background, collisionmap, speed=None):
        if speed is None:
            speed = self.speed
        if direction == 'UP':
            nx,ny = (self.pos[0],self.pos[1] - speed)
            if 0 < ny :
                if collisionmap.get_at((nx,ny))[3] == 0:
                    self.pos = (nx,ny)
        elif direction == 'DOWN':
            nx, ny = (self.pos[0], self.pos[1] + speed)
            if ny < background.get_height():
                if collisionmap.get_at((nx, ny))[3] == 0:
                    self.pos = (nx,ny)
        elif direction == 'LEFT':
            nx, ny = (self.pos[0] - speed, self.pos[1])
            if 0 < nx:
                if collisionmap.get_at((nx, ny))[3] == 0:
                    self.pos = (nx,ny)
        elif direction == 'RIGHT':
            nx, ny = (self.pos[0] + speed, self.pos[1])
            if nx < background.get_width():
                if collisionmap.get_at((nx, ny))[3] == 0:
                    self.pos = (nx,ny)

    def take_damage(self, amount):
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

    def render_player(self, sprites, game):
        sprite = transform.rotate(sprites[self.state][self.gif_counter // 10], self.rotation + 90)
        sprite = transform.smoothscale(sprite, (sprite.get_width() // 3, sprite.get_height() // 3))
        self.rect = game.screen.blit(sprite, (640 - sprite.get_width() // 2, 400 - sprite.get_height() // 2))

    def get_rect(self):
        return self.rect

    def get_pos(self):
        return self.pos

    def update_gif(self, sprites):
        if self.gif_counter >= 10 * len(sprites[self.state]) - 1:
            self.gif_counter = 0
        else:
            self.gif_counter += 1

def renderBullets(Game,player,gunType):
    for b in player.bullets:
        noCol = True
        px, py = player.pos
        nx = b[0][0] + 20*cos(radians(b[1]))#Position on entire map with the 20 pixel movement
        ny = b[0][1] - 20*sin(radians(b[1]))
        lx, ly = (nx - px + Game.screen.get_width() // 2, ny - py + Game.screen.get_height() // 2)#Position on screen
        interpolate = [(b[0][0] + i * cos(radians(b[1])), b[0][1] + i * sin(radians(b[1]))) for i in range(20)]
        if 0<lx<Game.screen.get_width() and 0<ly<Game.screen.get_height():
            for cx, cy in interpolate:#Checks if there's collision for the first 20 ish pixels
                if Game.collisionmap.get_at((int(cx), int(cy)))[3] != 0:
                    noCol = False

            if noCol:
                lb = transform.rotate(gunType.bulletSprite,b[1])
                Game.screen.blit(lb,(lx,ly))
                player.bullets[player.bullets.index(b)] = [(nx,ny),b[1]]#append changes
            else:
                del player.bullets[player.bullets.index(b)]
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
            interpolate = [(b[0][0] + i * cos(radians(b[1])), b[0][1] + i * sin(radians(b[1]))) for i in range(20)]
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
