import pickle
import socket
import threading
from math import *
from pygame import *
from random import*
import time as t
#Game constants--
TCP_IP = '127.0.0.1'#'159.203.147.141'
TCP_PORT = 4545
BUFFER_SIZE = 4096
#----------------
def check_health(player):
    'Function that checks if a player is dead'
    if player.health <= 0:
        return False
    return True

class Client:
    def __init__(self, player,drone, game, conn, sprites):
        'Networking object for this game'
        self.s = conn #Socket object "inherited" from menu code
        self.player = player
        self.game = game
        self.other_player_dict = dict() #Dictionary containing info of other players
        self.sprites = sprites
        self.drone = drone
        self.done = False #Flag for displaying victory screen

    def update_player(self, player):
        'Takes in "player" and updates it'
        self.player = player 
        
    def update_drone(self, drone):
        'Takes in "drone" and updates it'
        self.drone = drone
        
    def get_data(self):
        'Data transfer function'
        print('beginning transfer')
        while self.game.running:
            p = self.player
            p.update_gif(self.sprites)
            binary = pickle.dumps(p) #Convert player object to binary
            self.s.send(binary)
            data = self.s.recv(BUFFER_SIZE)
            data = pickle.loads(data)
            if data == 'winner': #Win process
                self.game.running = False #Shutoff game loop
                win = image.load('Background/victory.png')
                self.game.screen.blit(win, (1280//2-win.get_width()//2, #Blit in screen middle
                                      800//2-win.get_height()//2))
                display.flip()
                time.wait(1000)
                self.done = True
                return
            self.other_player_dict = data
            if len(self.other_player_dict[p.name].weapon_send)>0 and self.other_player_dict[p.name].weapon_send[0] =="Sent":
                p.weapon_send = []
            p.weapon_map = self.other_player_dict[p.name].weapon_map
            p.health = self.other_player_dict[p.name].health
            p.storm = self.other_player_dict[p.name].storm
            
<<<<<<< HEAD
            for b in self.other_player_dict[p.name].del_bullets:
                print(b[2])
                if b[2] == 'RPG':
                    p.rgif.append([b,0])
                    print("rpg")
=======
            for b in self.other_player_dict[p.name].del_bullets: #Remove bullets that belong to current player
>>>>>>> 5e397018f8ec42ca99a73b979c7eb9d0a6d5613c
                if b in p.bullets:
                    
                    p.bullets.remove(b)
                    
                        

    def render_other_players(self,Psprite=None):
        'Blit in other players'
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
                if px - g.screen.get_width() // 2 < ox < px + g.screen.get_width() \ #Only blit if other player is on screen
                        and py - g.screen.get_height() // 2 < oy < py + g.screen.get_height() // 2: 
                    other_sprite = transform.rotate(self.sprites[o.state][o.gif_counter //20%len(self.sprites[o.state])], o.rotation + 90) #Sprite appropriate for other player at their stage
                    nx = ox - px + g.screen.get_width() // 2 \ #Convert game coords to screen coords
                         - other_sprite.get_width() // 2
                    ny = oy - py + g.screen.get_height() // 2 \ #Same for y
                         - other_sprite.get_height() // 2
                    other_sprite = transform.rotate(self.sprites[o.state][o.gif_counter //20%len(self.sprites[o.state])], o.rotation + 90) #Rotate 
                    g.screen.blit(other_sprite, (nx,ny))
        if Psprite: #Displaying player for when drone is activated. Process is same as above
            px, py = p.get_pos()
            dx,dy = d.get_pos()
            if dx - g.screen.get_width() // 2 < px < dx + g.screen.get_width() //2 \
                        and dy - g.screen.get_height() // 2 < py < dy + g.screen.get_height() // 2:
                    your_Player = transform.rotate(Psprite[p.state][p.gif_counter//20%len(Psprite[p.state])], p.rotation + 90)
                    nx = px - dx + g.screen.get_width() // 2 \
                         - your_Player.get_width() // 2
                    ny = py - dy + g.screen.get_height() // 2 \
                         - your_Player.get_height() // 2
                    g.screen.blit(your_Player, (nx,ny))
                    
    def render_enemy_bullets(self, gun,screen):
        'Draw in enemy bullets'
        p = self.player
        g = self.game
        d = self.drone
        current = p
        if d != 0:
            current = d
        other_players = dict(zip(list(self.other_player_dict.keys()),list(self.other_player_dict.values()))) #Prevent dict changed size errors
        for o in other_players.values():
            if o.name != current.name:
                px, py = current.get_pos() #Position of player that fired bullets
                for b in o.bullets:
                    bx = b[0][0]
                    by = b[0][1]
                    lx, ly = (bx - px + g.screen.get_width() // 2, by - py + g.screen.get_height() // 2) #Convert game coords to screen coords
                    bullet_sprite = map_to_bullet(b[2], self.game) #Sprite
                    screen.blit(transform.rotate(bullet_sprite, b[1]), (lx, ly))

    def draw_weapons(self,screen,pos):
        'Draw guns lying on the ground'
        p = self.player
        #print(p.weapon_map)
        for i in p.weapon_map:
            if pos[0] - screen.get_width() // 2 < i[1][0] < pos[0] + screen.get_width() //2 \ #If on-screen
                        and pos[1] - screen.get_height() // 2 < i[1][1] < pos[1] + screen.get_height() // 2:
                image = self.game.weapon_dict[i[0]].inventory_image #Sprite
                nx = i[1][0] - pos[0] + screen.get_width() // 2 \ #Convert game coords to local coords
                         - image.get_width() // 2
                ny = i[1][1] - pos[1] + screen.get_height() // 2 \
                         - image.get_height() // 2
                screen.blit(image,(nx,ny))

    def weapon_pickup(self,inventory):
        'Pickup weapons'
        p = self.player
        for i in p.weapon_map:
            if hypot(i[1][0]-25-p.pos[0],i[1][1]-25-p.pos[1]) < 100: #Only pickup if gun is within 100px
                inventory.add_item(self.game.weapon_dict[i[0]],p,p.weapon_map,i) #Add to inventory
                #del self.weapon_map[self.weapon_map.index(i)]
                break

class GameMode:
    def __init__(self,server=False):
        'Logic backend for game'
        self.resolution = (1280,800)
        self.players = {}
        if not server: #Only initialize resources if instance isn't a server
            mixer.init()
            font.init()
            self.screen = display.set_mode(self.resolution)
            self.screen.fill((255,255,255))
            #Fonts--------------------------------------------
            self.title_font = font.Font('geonms-font.ttf', 72)
            self.textFont = font.Font('geonms-font.ttf', 32)
            #-------------------------------------------------
            background = transform.smoothscale(image.load('nmsplanet.jpg').convert(), (1280,800))
            self.screen.blit(background, (0, 0))
            title = self.title_font.render('outcast: the game', True, (255,255,255))
            txt = self.textFont.render('loading', True, (255,255,255))
            self.screen.blit(txt, (self.screen.get_width()//2-txt.get_width()//2, 550))
            self.screen.blit(title, (self.screen.get_width()//2-title.get_width()//2, 100))
            display.flip()
            self.music = mixer.music.load("Outcast.wav") #game music, currently unused
            self.background = image.load('Background/MapFinal.png').convert() #Actual game background
            self.droneB =False #Drone toggle flag
            self.drone_start = 31 #Drone cooldown in seconds
            self.current_actor = 0 #Initialize variable that remembers if drone or player
            self.surfaceALPHA = Surface((1280, 800), SRCALPHA) #Storm surface
            #Gun bullets and icons and data-------------------------------------------------------------------------------------------
            assaultrifle = Gun('AR',image.load('Weapons/lightbullet.png').convert_alpha(),
                               5,image.load('Weapons/machinegun.png').convert_alpha(),0,0.15)
            shotgun = Gun('Shotgun', image.load('Weapons/shellBullet.png').convert_alpha(),
                          10,image.load('Weapons/shotgunb.png').convert_alpha(), 6,0)
            sniper = Gun('Sniper',image.load('Weapons/heavyBullet.png').convert_alpha(),
                         25,image.load('Weapons/sniper.png').convert_alpha(),1,0)
            rpg = Gun('RPG',image.load('Weapons/rocketammo.png').convert_alpha(),50,image.load('Weapons/rpg.png').convert_alpha(),1,0)
            empty = Gun('Empty',0,0,image.load('Weapons/empty.png').convert_alpha(),0,0)
            self.weapon_dict = {"Shotgun":shotgun,"AR":assaultrifle,"Sniper":sniper,"RPG":rpg}
            self.guns = [assaultrifle,shotgun,sniper,rpg,empty,empty]
            #--------------------------------------------------------------------------------------------------------------------------
            self.buildingmap = image.load('Background/buildings.png').convert_alpha()
            self.building = False
            #weapon_list = [n.name for n in self.guns]
##            self.weapon_map =[]
##            for i in range(20):
##                weapon = choice(list(self.weapon_dict))
##                wx,wy = (randint(100,11900),randint(100,7900))
##                self.weapon_map.append([weapon,(wx,wy),100])
        else:
            #Background is needed for server-side authentication
            self.background = image.load('Background/MapFinal.png')
        self.collisionmap = image.load('Background/rocks+hole.png') #Collision map
        self.openbuilding = image.load('Background/openbuilding.png') #Building interiors
        self.running = True
        
    def draw_screen(self, player):
<<<<<<< HEAD
        'Draw in game UI and background'
        px,py = player.get_pos()
        portion = self.background.subsurface(Rect(px-self.screen.get_width()//2,  #Subsurfaced portion of 12K x 8K image
                                             py-self.screen.get_height()//2,
                                             self.screen.get_width(), self.screen.get_height()))
        self.screen.blit(portion, (0, 0))#First thing to blit
        #Storm
        if player.storm!=[]:
            draw.rect(self.surfaceALPHA,(0,0,255,80),(0,0,1280,800)) #Cover over for storm
            nx = int(player.storm[0][0]-player.pos[0]+self.screen.get_width()//2) #Game coords to screen coords
            ny = int(player.storm[0][1]-player.pos[1]+self.screen.get_height()//2)
            draw.circle(self.surfaceALPHA,(0,0,0,0),(nx,ny),int(player.storm[1])) #Draw in massive storm circle
            self.screen.blit(self.surfaceALPHA,(0,0))
        if player.health > 80: #Different colors for different health levels
            health_color = (0, 255, 0)
        elif player.health > 40:
            health_color = (255, 255, 0)
        else:
            health_color = (255, 0, 0)
        draw.rect(self.screen, 0, (20, 20, 300, 40), 2) #Base bar
        draw.rect(self.screen, health_color, (20, 20, int(player.health / 100 * 300), 40)) #Health amount bar
=======
        try:
            px,py = player.get_pos()
            portion = self.background.subsurface(Rect(px-self.screen.get_width()//2,
                                                 py-self.screen.get_height()//2,
                                                 self.screen.get_width(), self.screen.get_height()))
            self.screen.blit(portion, (0, 0))
            #Storm
            if player.storm!=[] or player.type == 'drone':
                draw.rect(self.surfaceALPHA,(0,0,255,80),(0,0,1280,800))
                nx = int(player.storm[0][0]-player.pos[0]+self.screen.get_width()//2)
                ny = int(player.storm[0][1]-player.pos[1]+self.screen.get_height()//2)
                draw.circle(self.surfaceALPHA,(0,0,0,0),(nx,ny),int(player.storm[1]))
                self.screen.blit(self.surfaceALPHA,(0,0))
            if player.health > 80:
                health_color = (0, 255, 0)
            elif player.health > 40:
                health_color = (255, 255, 0)
            else:
                health_color = (255, 0, 0)
            draw.rect(self.screen, 0, (20, 20, 300, 40), 2)
            draw.rect(self.screen, health_color, (20, 20, int(player.health / 100 * 300), 40))
>>>>>>> df384e14753577e77ee9318908ed7e9f81633d30

        #Minimap
        minimap = transform.scale(self.background,(180,120)) #scale down map size for minimap
        self.screen.blit(minimap,(1050,50))
        draw.circle(self.screen,(255,0,0),(int(1050+(px/12000)*180),int(50+(py/8000)*120)),2)
        if player.storm!=[]:#If storm exists
            if len(player.storm) == 5:
                draw.circle(self.screen,(0,0,255),(int(1050+(player.storm[0][0]/12000)*180),int(50+(player.storm[0][1]/8000)*120)),int(player.storm[1]//67),2)
                draw.circle(self.screen,(0,255,0),(int(1050+(player.storm[3][0]/12000)*180),int(50+(player.storm[3][1]/8000)*120)),int(player.storm[4]//67),2)
            elif len(player.storm) == 3:
                draw.circle(self.screen,(0,0,255),(int(1050+player.storm[0][0]/12000*180),int(50+(player.storm[0][1]/8000)*120)),int(player.storm[1]//67),2)

    def drone_click(self,g,p,client):
        'Activate drone and process action'
        if self.droneB == False and t.time()-self.drone_start >30:#If the cooldown is down, run
            self.drone = Drone(g, '%s' % ("ID"), (p.pos), 6, 'drone') #Create drone object
            self.current_actor = self.drone #Set current mode to drone object
            client.drone = self.drone #Give networking system access to drone object
            self.droneB = True #Flip flag
            self.drone_start=t.time() #Remember start time for cooldown
        elif self.droneB == False and t.time()-self.drone_start <30: #cancel function if it's still on cooldown
            pass
        else: #This means we're deactivating the drone
            self.drone_start=t.time() #Use this for cooldown
            #Reset variables-------
            client.drone = 0
            self.current_actor = p
            self.droneB = False
<<<<<<< HEAD
            #----------------------
    def open_door(self,p):
        if self.openbuilding.get_at((p.pos[0],p.pos[1]))[3] != 0:
            self.building = True
            print("open")
=======
    
##    def draw_weapons(self,screen,pos):
##        for i in self.weapon_map:
##            if pos[0] - screen.get_width() // 2 < i[1][0] < pos[0] + screen.get_width() //2 \
##                        and pos[1] - screen.get_height() // 2 < i[1][1] < pos[1] + screen.get_height() // 2:
##                image = self.weapon_dict[i[0]].inventory_image
##                nx = i[1][0] - pos[0] + screen.get_width() // 2 \
##                         - image.get_width() // 2
##                ny = i[1][1] - pos[1] + screen.get_height() // 2 \
##                         - image.get_height() // 2
##                screen.blit(image,(nx,ny))
##
##
##    def weapon_pickup(self,p,inventory):
##        for i in self.weapon_map:
##            if hypot(i[1][0]-25-p.pos[0],i[1][1]-25-p.pos[1]) <100:
##                inventory.add_item(self.weapon_dict[i[0]],p,self.weapon_map,i)
##                del self.weapon_map[self.weapon_map.index(i)]
##                break
>>>>>>> df384e14753577e77ee9318908ed7e9f81633d30
                
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
        self.weapon_send = []#[weapon to remove, weapon to add]
        self.type = mode
        self.weapon_map = []
        self.storm = []
        self.building = False
        self.rocket_b = []
        self.rgif = []
    def move(self, direction, background, collisionmap,buildingmap,openbuilding, FPS, speed=None):
        wall = ((150,72,15))
        if speed is None:
            speed = self.speed
        speed = int(speed/FPS*60)
        
        if direction == 'UP':
            nx,ny = (self.pos[0],self.pos[1] - speed)
            if self.building and openbuilding.get_at((nx,ny))[3] == 0:
                self.building = False
            if 0 < ny :
                if collisionmap.get_at((nx,ny))[3] == 0 and buildingmap.get_at((nx,ny))[3] == 0 or (self.building == True and openbuilding.get_at((nx,ny)) != wall):
                    self.pos = (nx,ny)
        elif direction == 'DOWN':
            nx, ny = (self.pos[0], self.pos[1] + speed)
            if self.building and openbuilding.get_at((nx,ny))[3] == 0:
                self.building = False
            if ny < background.get_height():
                if collisionmap.get_at((nx, ny))[3] == 0 and buildingmap.get_at((nx,ny))[3] == 0 or (self.building == True and openbuilding.get_at((nx,ny)) != wall):
                    self.pos = (nx,ny)
        elif direction == 'LEFT':
            nx, ny = (self.pos[0] - speed, self.pos[1])
            if self.building and openbuilding.get_at((nx,ny))[3] == 0:
                building = False
            if 0 < nx:
                if collisionmap.get_at((nx, ny))[3] == 0 and buildingmap.get_at((nx,ny))[3] == 0 or (self.building == True and openbuilding.get_at((nx,ny)) != wall):
                    self.pos = (nx,ny)
        elif direction == 'RIGHT':
            nx, ny = (self.pos[0] + speed, self.pos[1])
            if self.building and openbuilding.get_at((nx,ny))[3] == 0:
                self.building = False
            if nx < background.get_width():
                if collisionmap.get_at((nx, ny))[3] == 0 and buildingmap.get_at((nx,ny))[3] == 0 or (self.building == True and openbuilding.get_at((nx,ny)) != wall):
                    self.pos = (nx,ny)
    def open_door(self,openbuilding):
        if openbuilding.get_at((self.pos[0],self.pos[1]))[3] != 0:
            self.building = True
            print("open")
    def take_damage(self, amount):
        if self.health-amount > 0:
            self.health -= amount
            
    def die(self, screen):
        wasted = image.load('wasted.png').convert()
        wasted = transform.smoothscale(wasted, (1280,800))
        screen.blit(wasted, (0,0))
        print("dead")

    def fire(self, inventory, FPS):
        if inventory.inventoryP[inventory.state].name != 'Empty' and self.ammo[inventory.state]>0:
            try:
                ratio = int(20/FPS*60)
            except ZeroDivisionError:
                ratio = 1
            px, py = self.pos
            self.ammo[inventory.state] -=1
            if inventory.inventoryP[inventory.state].spread > 1:
                #print(inventory.inventoryP[inventory.state].spread)
                for a in range(1,inventory.inventoryP[inventory.state].spread):
                    spread = self.rotation+90-(3-a)*6
                    self.bullets.append([(px+5*cos(radians(spread)), py-5*sin(radians(spread))), spread, inventory.inventoryP[inventory.state].name, ratio])
            else:
                angle = self.rotation+90
                self.bullets.append([(px+5*cos(radians(angle)), py-5*sin(radians(angle))), angle, inventory.inventoryP[inventory.state].name, ratio])               
                
    def render_player(self, sprites, game):
        sprite = transform.rotate(sprites[self.state][self.gif_counter//20%len(sprites[self.state])], self.rotation + 90)
        self.rect = game.screen.blit(sprite, (640 - sprite.get_width() // 2, 400 - sprite.get_height() // 2))
    def rocket_animation(self,screen,anim):
        print(self.rgif)
        for i in self.rgif:
            if i[0][0][0] - screen.get_width() // 2 < p.pos[0] < i[0][0][0] + screen.get_width() //2 \
                        and i[0][0][1] - screen.get_height() // 2 < p.pos[1] < i[0][0][1] + screen.get_height() // 2:
                bullet_sprite = anim[i[1]//20%len(anim)]
                print(bullet_sprite,i[0][0])
                lx, ly = (i[0][0][0] - self.pos[0] + screen.get_width() // 2, i[0][0][1] - self.pos[1] + screen.get_height() // 2)
                screen.blit(bullet_sprite, (lx,ly))
            if i[1] <30:
                self.rgif[self.rgif.index(i)][1]+=1
            else:
                del self.rgif[self.rgif.index(i)]
            

    def get_rect(self):
        return self.rect

    def get_pos(self):
        return self.pos

    def update_gif(self, sprites, server=False):
        self.gif_counter += 1
    def player_state(self,inventory):
        if inventory.inventoryP[inventory.state].name == "Empty":
            self.state = 0
        else:
            self.state = 2

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
    #The Storm
    
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
        try:
            delta = int(20/FPS*60)
        except ZeroDivisionError:
            delta = 20
        nx = bx + delta*cos(radians(b[1]))#Position on entire map with the 20 pixel movement
        ny = by - delta*sin(radians(b[1]))
        lx, ly = (nx - px + Game.screen.get_width() // 2, ny - py + Game.screen.get_height() // 2)#Position on screen
        interpolate = [(b[0][0] - i * cos(radians(b[1])), b[0][1] + i * sin(radians(b[1]))) for i in range(delta)]#Checks if there's collsion within 20 px
         
        if 0 < lx < Game.screen.get_width() and 0 < ly < Game.screen.get_height():
            hit_detected = False
            for cx, cy in interpolate:
                if Game.collisionmap.get_at((int(cx), int(cy)))[3] != 0 or Game.buildingmap.get_at((int(cx),int(cy)))[3] !=0:
                    no_collision = False
                    break
                for o in client.other_player_dict.values():
                    if o.name != player.name:
                        ox, oy = o.pos
                        if hypot(ox-cx, oy-cy) < 30:
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

    def add_item(self,item,p,weaponm,d):
        #inventory.add_item(self.weapon_dict[i[0]],p,self.weapon_map[self.weapon_map.index(i)][2],self.weapon_map)
        ammo = weaponm[weaponm.index(d)][2]
        inventoryF = [i.name for i in self.inventoryP]
        if  "Empty" in inventoryF:
            p.weapon_send = [d,0]
            p.ammo[inventoryF.index("Empty")] = ammo
            self.inventoryP[inventoryF.index("Empty")] = item
        else:
            p.weapon_send = [d,[self.inventoryP[self.state].name,(p.pos),p.ammo[self.state]]]
            #weaponm.append([self.inventoryP[self.state].name,(p.pos),p.ammo[self.state]])
            self.inventoryP[self.state] = item
            p.ammo[self.state] = ammo
            
    def remove_item(self,p):
        if self.inventoryP[self.state].name == "Empty":
            pass
        else:
            p.weapon_send = [0,[self.inventoryP[self.state].name,(p.pos),p.ammo[self.state]]]
            self.inventoryP[self.state] = self.empty
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
