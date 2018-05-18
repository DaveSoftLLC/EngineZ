import pickle
import socket
import threading
from math import *
from pygame import *

TCP_IP = '127.0.0.1'
TCP_PORT = 4545
BUFFER_SIZE = 5000


class Client:
    def __init__(self, player,drone, game, TCP_IP, TCP_PORT, sprites):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player = player
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.game = game
        self.other_player_dict = dict()
        self.sprites = sprites
        self.drone = drone

    def update_player(self, player):
        self.player = player
    def update_drone(self, drone):
        self.drone = drone
    def get_data(self):
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
    #will be compressed later
    def render_other_players(self,Psprite=None):
        p = self.player
        g = self.game
        d = self.drone
        if d == 0:
            for o in self.other_player_dict.values():
                if o.name != p.name:
                    px, py = p.get_pos()
                    ox, oy = o.get_pos()
                    if px - g.screen.get_width() // 2 < ox < px + g.screen.get_width() \
                            and py - g.screen.get_height() // 2 < oy < py + g.screen.get_height() // 2:
                        other_sprite = transform.rotate(self.sprites[o.state][o.gif_counter // 10], o.rotation + 90)
                        other_sprite = transform.smoothscale(other_sprite, (
                            other_sprite.get_width() // 3,
                            other_sprite.get_height() // 3))
                        nx = ox - px + g.screen.get_width() // 2 \
                             - other_sprite.get_width() // 2
                        ny = oy - py + g.screen.get_height() // 2 \
                             - other_sprite.get_height() // 2
                        other_sprite = transform.rotate(self.sprites[o.state][o.gif_counter // 10], o.rotation + 90)
                        other_sprite = transform.smoothscale(other_sprite, (
                            other_sprite.get_width() // 3,
                            other_sprite.get_height() // 3))
                        g.screen.blit(other_sprite, (nx,ny))
        else:
            for o in self.other_player_dict.values():
                if o.name != d.name:
                    dx, dy = d.get_pos()
                    ox, oy = o.get_pos()
                    if dx - g.screen.get_width() // 2 < ox < dx + g.screen.get_width() //2 \
                            and dy - g.screen.get_height() // 2 < oy < dy + g.screen.get_height() // 2:
                        other_sprite = transform.rotate(self.sprites[o.state][o.gif_counter // 10], o.rotation + 90)
                        other_sprite = transform.smoothscale(other_sprite, (
                            other_sprite.get_width() // 3,
                            other_sprite.get_height() // 3))
                        nx = ox - dx + g.screen.get_width() // 2 \
                             - other_sprite.get_width() // 2
                        ny = oy - dy + g.screen.get_height() // 2 \
                             - other_sprite.get_height() // 2

                        g.screen.blit(other_sprite, (nx,ny))
            px, py = p.get_pos()
            dx,dy = d.get_pos()
            if dx - g.screen.get_width() // 2 < px < dx + g.screen.get_width() //2 \
                            and dy - g.screen.get_height() // 2 < py < dy + g.screen.get_height() // 2:
                        your_Player = transform.rotate(Psprite[p.state][p.gif_counter // 10], p.rotation + 90)
                        your_Player = transform.smoothscale(your_Player, (
                            your_Player.get_width() // 3,
                            your_Player.get_height() // 3))
                        nx = px - dx + g.screen.get_width() // 2 \
                             - your_Player.get_width() // 2
                        ny = py - dy + g.screen.get_height() // 2 \
                             - your_Player.get_height() // 2

                        g.screen.blit(your_Player, (nx,ny))

    def render_enemy_bullets(self, gun):
        p = self.player
        g = self.game
        d = self.drone
        current = p
        if d != 0:
            current = d
        for o in self.other_player_dict.values():
            if o.name != current.name:
                px, py = current.get_pos()
                for b in o.bullets:
                    bx = b[0][0]
                    by = b[0][1]
                    for a in range(1, 6):
                        angle = b[1] + 90 - (3 - a) * 6
                        lb = transform.rotate(gun.bulletSprite, angle)
                        lx, ly = (bx - px + g.screen.get_width() // 2, by - py + g.screen.get_height() // 2)
                        g.screen.blit(lb, (lx, ly))

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
            self.screen.blit(portion, (0, 0))

            if player.health > 80:
                health_color = (0, 255, 0)
            elif player.health > 40:
                health_color = (255, 255, 0)
            else:
                health_color = (255, 0, 0)
            draw.rect(self.screen, 0, (20, 20, 300, 40), 2)
            draw.rect(self.screen, health_color, (20, 20, player.health / 100 * 300, 40))
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
        px, py = self.pos
        self.bullets.append(
            [(px + 5 * cos(radians(self.rotation)), py - 5 * sin(radians(self.rotation))), self.rotation])

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

class Drone(Player):
    def printdrone():
        print("I don't know what extra functions to put in yet")

def render_bullets(Game, player, gunType):
    for b in player.bullets:
        no_collision = True
        px, py = player.pos
        nx = b[0][0] + 20*cos(radians(b[1]))#Position on entire map with the 20 pixel movement
        ny = b[0][1] - 20*sin(radians(b[1]))
        lx, ly = (nx - px + Game.screen.get_width() // 2, ny - py + Game.screen.get_height() // 2)#Position on screen
        interpolate = [(b[0][0] - i * cos(radians(b[1])), b[0][1] + i * sin(radians(b[1]))) for i in range(20)]
        if 0 < lx < Game.screen.get_width() and 0 < ly < Game.screen.get_height():
            for cx, cy in interpolate:
                if Game.collisionmap.get_at((int(cx), int(cy)))[3] != 0:
                    no_collision = False
                    break

            if no_collision:
                for a in range(1, 6):
                    angle = b[1] + 90 - (3 - a) * 6
                    lb = transform.rotate(gunType.bulletSprite, angle)
                    Game.screen.blit(lb, (lx, ly))
                player.bullets[player.bullets.index(b)] = [(nx, ny), b[1]]
            else:
                del player.bullets[player.bullets.index(b)]
        else:
            del player.bullets[player.bullets.index(b)]


def render_enemy_bullets(Game, userplayer, players, gunType):
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
                    for a in range(1, 6):
                        angle = b[1] + 90 - (3 - a) * 6
                        lb = transform.rotate(gunType.bulletSprite, angle)
                        Game.screen.blit(lb, (lx, ly))
                    player.bullets[player.bullets.index(b)] = [(nx, ny), b[1]]  # append changes
            else:
                del player.bullets[player.bullets.index(b)]


class Inventory:
    def __init__(self, i0, i1, i2, i3, i4, i5):
        self.inventoryP = [i0, i1, i2, i3, i4, i5]
        self.state = 0

    def add_item(self,item):
        if 0 in self.inventoryP:
            self.inventoryP[self.inventoryP.index(0)] = item
        else:
            self.inventoryP[self.state] = item
        #Visually remove or add object needs to be done
    
    def switch(self,scroll):
        if scroll == "RIGHT":
            if len(self.inventoryP) == self.state+1:
                self.state = 0
            else:
                self.state += 1
        else:
            if 0 == self.state:
                self.state = 5
            else:
                self.state-=1
        print(self.state)

    def draw_inventory(self,Game):
        for i in range(6):
            if i!=self.state:
                Game.blit(self.inventoryP[i].inventory_image,(850+i*69,700))
                draw.rect(Game,(0),(850+i*69,700,70,70),2)
        Game.blit(self.inventoryP[self.state].inventory_image,(850+self.state*69,695))
        draw.rect(Game,(0,0,255),(850+self.state*69,695,70,70),2)


class Gun:
    def __init__(self, name, bulletSprite, damage, inventory_image, spread=None):
        self.name = name
        self.bulletSprite = bulletSprite
        self.damage = damage
        self.spread = spread
        self.inventory_image = inventory_image        
