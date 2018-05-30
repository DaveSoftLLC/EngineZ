import pickle
import socket
import threading
from math import *
from pygame import *
from random import*
import time as t

TCP_IP = '127.0.0.1'#'159.203.147.141'
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
            p.update_gif(self.sprites)
            binary = pickle.dumps(p)
            self.s.send(binary)
            data = self.s.recv(BUFFER_SIZE)
            data = pickle.loads(data)
            self.other_player_dict = data
            p.health = self.other_player_dict[p.name].health
            for b in self.other_player_dict[p.name].del_bullets:
                if b in p.bullets:
                    p.bullets.remove(b)
        self.s.close()
        
    def render_other_players(self,Psprite=None):
        p = self.player
        g = self.game
        d = self.drone
        current = p
        if Psprite:
            current = d
        for o in self.other_player_dict.values():
            if o.name != current.name:
                px, py = current.get_pos()
                ox, oy = o.get_pos()
                if px - g.screen.get_width() // 2 < ox < px + g.screen.get_width() \
                        and py - g.screen.get_height() // 2 < oy < py + g.screen.get_height() // 2:
                    other_sprite = transform.rotate(self.sprites[o.state][o.gif_counter // 10], o.rotation + 90)

                    nx = ox - px + g.screen.get_width() // 2 \
                         - other_sprite.get_width() // 2
                    ny = oy - py + g.screen.get_height() // 2 \
                         - other_sprite.get_height() // 2
                    other_sprite = transform.rotate(self.sprites[o.state][o.gif_counter // 10], o.rotation + 90)

                    g.screen.blit(other_sprite, (nx,ny))
        if Psprite: #displaying player
            px, py = p.get_pos()
            dx,dy = d.get_pos()
            if dx - g.screen.get_width() // 2 < px < dx + g.screen.get_width() //2 \
                        and dy - g.screen.get_height() // 2 < py < dy + g.screen.get_height() // 2:
                    your_Player = transform.rotate(Psprite[p.state][p.gif_counter // 10], p.rotation + 90)
                    nx = px - dx + g.screen.get_width() // 2 \
                         - your_Player.get_width() // 2
                    ny = py - dy + g.screen.get_height() // 2 \
                         - your_Player.get_height() // 2
                    g.screen.blit(your_Player, (nx,ny))
                    
    def render_enemy_bullets(self, gun,screen):
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
##                    for a in range(1, 6):
##                        angle = b[1] + 90 - (3 - a) * 6
                    
                    #lb = transform.rotate(gun.bulletSprite, b[1])
                    lx, ly = (bx - px + g.screen.get_width() // 2, by - py + g.screen.get_height() // 2)
                    bullet_sprite = map_to_bullet(b[2], Game)
                    screen.blit(transform.rotate(bullet_sprite, b[1]), (lx, ly))
                    #gunType.gun_Bullet(b[2],lx,ly,b[1],screen)
                    #g.screen.blit(lb, (lx, ly))

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
            self.background = image.load('Background/MapFinal.png').convert()
            self.droneB =False
            self.drone_start = 31
            
            self.current_actor = 0
            assaultrifle = Gun('AR',image.load('Weapons/lightbullet.png').convert_alpha(),
                               5,image.load('Weapons/machinegun.png').convert_alpha(),0,0.15)
            shotgun = Gun('Shotgun', image.load('Weapons/shellBullet.png').convert_alpha(),
                          10,image.load('Weapons/shotgunb.png').convert_alpha(), 6,0)
            sniper = Gun('Sniper',image.load('Weapons/heavyBullet.png').convert_alpha(),
                         25,image.load('Weapons/sniper.png').convert_alpha(),1,0)
            empty = Gun('Empty',0,0,image.load('Weapons/empty.png').convert_alpha(),0,0)
            self.weapon_dict = {"Shotgun":shotgun,"AR":assaultrifle,"Sniper":sniper}
            self.guns = [assaultrifle,shotgun,sniper,empty,empty,empty]
            #weapon_list = [n.name for n in self.guns]
            self.weapon_map =[]
            for i in range(20):
                weapon = choice(list(self.weapon_dict))
                wx,wy = (randint(100,11900),randint(100,7900))
                self.weapon_map.append([weapon,(wx,wy)])
        else:
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

    def drone_click(self,g,p,client):
        if self.droneB == False and t.time()-self.drone_start >30:#If the cooldown is down, run
            self.drone = Drone(g, '%s' % ("ID"), (p.pos), 6, 'drone')
            self.current_actor = self.drone
            client.drone = self.drone
            self.droneB = True
            self.drone_start=t.time()
        elif self.droneB == False and t.time()-self.drone_start <30:
            pass
        else:
            self.drone_start=t.time()
            client.drone = 0
            self.current_actor = p
            self.droneB = False

    def weapon_pickup(self,p,inventory):
        for i in self.weapon_map:
            if hypot(i[1][0]-p.pos[0],i[1][1]-p.pos[1]) <30:
                inventory.add_item(self.weapon_dict[i[0]],p)
                print("item added")
        print(p.pos)
        print(self.weapon_map)

class Player:
    def __init__(self, game, name, pos, speed, mode):
        self.name = name
        self.pos = pos
        self.rotation = 90
        self.state = 0
        self.health = 100
        self.speed = speed
        self.bullets = []
        self.rect = None
        self.gif_counter = 0
        self.del_bullets = []
        self.ammo = []
        self.type = mode

    def move(self, direction, background, collisionmap, FPS, speed=None):
        if speed is None:
            speed = self.speed
        speed = int(speed/FPS*60)
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

    def fire(self, inventory, FPS):
        if inventory.inventoryP[inventory.state].name != 'Empty' and self.ammo[inventory.state]>0:
            
            px, py = self.pos
            self.ammo[inventory.state] -=1
            
            if inventory.inventoryP[inventory.state].spread > 1:
                #print(inventory.inventoryP[inventory.state].spread)
                for a in range(1,inventory.inventoryP[inventory.state].spread):
                    spread = self.rotation+90-(3-a)*6
                    self.bullets.append([(px+5*cos(radians(spread)), py-5*sin(radians(spread))), spread, inventory.inventoryP[inventory.state].name, int(20/FPS*60)])
            else:
                angle = self.rotation+90
                self.bullets.append([(px+5*cos(radians(angle)), py-5*sin(radians(angle))), angle, inventory.inventoryP[inventory.state].name, int(20/FPS*60)])               
                
        

    def render_player(self, sprites, game):
        sprite = transform.rotate(sprites[self.state][self.gif_counter // 10], self.rotation + 90)
        self.rect = game.screen.blit(sprite, (640 - sprite.get_width() // 2, 400 - sprite.get_height() // 2))

    def get_rect(self):
        return self.rect

    def get_pos(self):
        return self.pos

    def update_gif(self, sprites, server=False):
        if self.gif_counter >= 10 * len(sprites[self.state]) - 1:
            self.gif_counter = 0
        elif not server:
            self.gif_counter += 1

class Drone(Player):
    def draw_drone(Game,droneB,piclist,timer):
        textFont = font.SysFont("Arial", 18)
        if timer>30 and droneB == False:#When cooldown is done
            dronebutton = piclist[0]

        elif droneB == False and timer<30:#Cooldown till you can use it again
            dronebutton = piclist[1]
            Game.blit(textFont.render(str(round(30-timer,2)), True, (255,255,255)), (35, 770))
            
        elif droneB == True: #Timer for while using drone
            dronebutton = piclist[1]
            Game.blit(textFont.render(str(round(10-timer,2)), True, (255,255,255)), (35, 770))

        Game.blit(dronebutton,(20,700))
        
        
    ##########
    #To put in:
    #Trees that can be broken down (randint tree rect)
    #Randomize pickup of weapons and pickup
    
def map_to_bullet(name,game):
    for n in game.guns:
        if name == n.name:
            return n.bulletSprite
    return None

def render_bullets(Game, player, client, FPS):
    for b in player.bullets:
        no_collision = True
        px, py = player.pos
        bx, by = b[0]
        delta = int(20/FPS*60)
        nx = bx + delta*cos(radians(b[1]))#Position on entire map with the 20 pixel movement
        ny = by - delta*sin(radians(b[1]))
        lx, ly = (nx - px + Game.screen.get_width() // 2, ny - py + Game.screen.get_height() // 2)#Position on screen
        interpolate = [(b[0][0] - i * cos(radians(b[1])), b[0][1] + i * sin(radians(b[1]))) for i in range(delta)]#Checks if there's collsion within 20 px
         
        if 0 < lx < Game.screen.get_width() and 0 < ly < Game.screen.get_height():
            hit_detected = False
            for cx, cy in interpolate:
                if Game.collisionmap.get_at((int(cx), int(cy)))[3] != 0:
                    no_collision = False
                    break
                for o in client.other_player_dict.values():
                    if o.name != player.name:
                        ox, oy = o.pos
                        if hypot(ox-cx, oy-cy) < 30:
##                            other_sprite = transform.rotate(client.sprites[o.state][o.gif_counter // 10], o.rotation + 90)
##                            ox = ox - px + Game.screen.get_width() // 2 \
##                                 - other_sprite.get_width() // 2
##                            oy = oy - py + Game.screen.get_height() // 2 \
##                                 - other_sprite.get_height() // 2
##                            if hypot(ox-cx, oy-cy) < max(other_sprite.get_size()):
##                                gunType.gun_Bullet(b[2],cx,cy,b[1],Game.screen)#What is this for? cx and cy are outside screen
##                                
##                                #bullet_sprite = transform.rotate(gunType.bulletSprite, b[1])
##                                #Game.screen.blit(bullet_sprite, (cx, cy))
                            try:
                                player.bullets.remove(b)

                            except ValueError:
                                pass
                            hit_detected = True
                            break
                if hit_detected:
                    break
            if no_collision:
        
                try: #faster than doing 'if not in', because that takes O(N) time
                    player.bullets[player.bullets.index(b)] = [(nx, ny), b[1],b[2], delta]
                except ValueError:
                    pass
                bullet_sprite = map_to_bullet(b[2], Game)
                Game.screen.blit(transform.rotate(bullet_sprite, b[1]), (lx, ly))
                #bullet_sprite = transform.rotate(gunType.bulletSprite, b[1])
                #Game.screen.blit(bullet_sprite, (lx, ly))
            else:
                player.bullets.remove(b)
        elif hypot(px-nx, py-ny) < 1500:
            player.bullets[player.bullets.index(b)] = [(nx, ny), b[1],b[2], delta]
        else:
            player.bullets.remove(b)

class Inventory:
    def __init__(self, items):
        self.inventoryP = items
        self.state = 0
        self.textFont = font.SysFont("Arial", 22)
        self.empty = Gun('Empty',0,0,image.load('Weapons/empty.png').convert_alpha(),0,0)

    def add_item(self,item,p):
        if  self.empty in self.inventoryP:
            self.inventoryP[self.inventoryP.index(self.empty)] = item
            p.ammo[self.inventoryP.index(self.empty)] = 100
        else:
            self.inventoryP[self.state] = item
            p.ammo[self.state] = 100
        #Visually remove or add object needs to be done
    
    def switch(self,scroll):
        if scroll == "RIGHT":
            if len(self.inventoryP) == self.state+1:
                self.state = 0
            else:
                self.state += 1
        else:
            if 0 == self.state:
                self.state = len(self.inventoryP)-1
            else:
                self.state-=1

    def draw_inventory(self,Game,ammo):
        for i in range(len(self.inventoryP)):
            if i!=self.state:
                Game.blit(self.inventoryP[i].inventory_image,(850+i*69,700))
                Game.blit(self.textFont.render(str(ammo[i]), True, (255,255,255)), (850+i*69,700))
                draw.rect(Game,(0),(850+i*69,700,70,70),2)
        Game.blit(self.inventoryP[self.state].inventory_image,(850+self.state*69,695))
        Game.blit(self.textFont.render(str(ammo[self.state]), True, (255,255,255)), (850+self.state*69,695))
        draw.rect(Game,(0,0,255),(850+self.state*69,695,70,70),2)
        

class Gun:
    def __init__(self, name, bulletSprite, damage, inventory_image, spread,rate):
        self.name = name
        self.bulletSprite = bulletSprite
        self.damage = damage
        self.spread = spread
        self.inventory_image = inventory_image
        self.rate = rate
        self.gundict = {'Shotgun':image.load('Weapons/shellBullet.png'),'AR':image.load('Weapons/lightbullet.png'),'Sniper':image.load('Weapons/heavyBullet.png')}
    def gun_Bullet(self, name, x,y,rot,Game):
        if name!='Empty':
            bullet_sprite = transform.rotate(self.gundict[name], rot)
            Game.blit(bullet_sprite, (x,y))
        
##    def gun_Bullet(self, name, x,y,rot,Game):
##        if name!='Empty':
##            
##            bullet_sprite = transform.rotate(self.bulletSprite, rot)
##            Game.blit(bullet_sprite, (x,y))
##        
