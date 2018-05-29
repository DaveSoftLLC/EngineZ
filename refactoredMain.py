import glob
from random import randint

from BaseGame import *
import time as t
g = GameMode()
assaultrifle = Gun('AR',image.load('Weapons/lightbullet.png').convert_alpha(),5,image.load('Weapons/machinegun.png').convert_alpha(),0,0.05)
shotgun = Gun('Shotgun', image.load('Weapons/shellBullet.png').convert_alpha(), 10,image.load('Weapons/shotgunb.png').convert_alpha(), 6,0)
empty = Gun('Empty',0,0,image.load('Weapons/empty.png').convert_alpha(),0,0)

inventory = Inventory(shotgun,shotgun,shotgun,assaultrifle,shotgun,empty)
dronebuttonlist = [image.load("Background/dronebutton.png"),image.load("Background/dronebuttondark.png")]

collision = image.load('Background/rocks+hole.png').convert_alpha()
def scale_and_load(path, factor):
    img = image.load(path).convert_alpha()
    x, y = img.get_size()
    return transform.smoothscale(img, (int(x/factor), int(y/factor)))
def get_fps(old_time):
    return int(1/(t.time()-old_time))
sprites = [image.load('Sprites/sprite1.png'), image.load('Sprites/sprite2.png'), image.load('Sprites/sprite3.png')]
newSprites = [[scale_and_load(file, 3) for file in glob.glob('newSprites/shotgun/idle/*.png')],
              [scale_and_load(file, 3) for file in glob.glob('newSprites/shotgun/move/*.png')],
              [scale_and_load(file, 3) for file in glob.glob('newSprites/shotgun/shoot/*.png')]]

droneSprite = [[scale_and_load(file, 2) for file in glob.glob('newSprites/drone/*.png')]]
droneB = False
p = Player(g, '%d' % (randint(1, 100)), (1200, 1200), 10, 'player')
client = Client(p,0,g, TCP_IP, 4545, newSprites)
threading.Thread(target=client.get_data).start()
drone_start = 31 #Drone can be used first (30 seconds)
fps_font = font.SysFont('Arial',18)
current_actor = p
myClock = time.Clock()
last_fire = 0
while g.running:
    myClock.tick(144)
    FPS = myClock.get_fps()
    if inventory.inventoryP[inventory.state].rate >0 and m[0] == 1:
        left_click = True
    else:
        left_click = False
    for e in event.get():
        if e.type == QUIT:
            g.running = False
        if e.type == MOUSEBUTTONDOWN:
            if droneB == False:
                if e.button == 1:
                    left_click = True
                elif e.button == 5: #scroll to move right
                    inventory.switch("RIGHT")
                elif e.button == 4:#scroll to move left
                    inventory.switch("LEFT")
        elif e.type == KEYDOWN:
            keys = key.get_pressed()
            if keys[K_z]:
                if droneB == False and t.time()-drone_start >30:#If the cooldown is down, run
                    drone = Drone(g, '%s' % ("ID"), (p.pos), 6, 'drone')
                    current_actor = drone
                    client.drone = drone
                    droneB = True
                    drone_start=t.time()
                elif droneB == False and t.time()-drone_start <30:
                    pass
                else:
                    drone_start=t.time()
                    client.drone = 0
                    current_actor = p
                    droneB = False
    m = mouse.get_pressed()
    mx, my = mouse.get_pos()
    
    keys = key.get_pressed()
    old_time = t.time()
    if 1:
        current_actor.rotation = int(degrees(atan2((g.screen.get_width()//2-mx),(g.screen.get_height()//2-my))))
        px, py = current_actor.get_pos()
        #SPRINT only for player
        if keys[K_LSHIFT] and m[0] == 1:
            p.speed = 5
            p.state = 2
        elif keys[K_LSHIFT]:
            p.speed = 13
            p.state = 1
        else:
            p.speed = 10
            p.state = 0

        #UP
        if keys[K_w] and g.screen.get_height()//2<py-current_actor.speed:
            current_actor.move('UP', g.background, g.collisionmap, FPS)
        #DOWN
        if keys[K_s] and py+p.speed<g.background.get_height()-g.screen.get_height()//2:
            current_actor.move('DOWN', g.background, g.collisionmap, FPS)
        #LEFT
        if keys[K_a] and g.screen.get_width()//2<px-current_actor.speed:
            current_actor.move('LEFT', g.background, g.collisionmap, FPS)
        #RIGHT
        if keys[K_d] and px+current_actor.speed<g.background.get_width()-g.screen.get_width()//2:
            current_actor.move('RIGHT', g.background, g.collisionmap, FPS)

        if current_actor.type == 'player' and left_click and (t.time() - last_fire > 0.3 or (inventory.inventoryP[inventory.state].rate >0 and t.time() - last_fire > inventory.inventoryP[inventory.state].rate)):
            last_fire = t.time()
            p.state = 2
            p.fire(inventory, FPS)
            """
            if inventory.inventoryP[inventory.state].rate >0:
                left_click = True
            else:
                left_click = False
            """
        g.draw_screen(current_actor)
        if current_actor.type == 'player':
            p.update_gif(newSprites)
            p.render_player(newSprites, g)
            client.render_other_players()
            client.update_player(p)
        else:
            client.render_other_players(newSprites)
            client.update_drone(drone)
            drone.update_gif(droneSprite)
            drone.render_player(droneSprite, g)
            #If time runs out
            if t.time()-drone_start >10:
                client.drone = 0
                current_actor = p
                drone_start = t.time()
                droneB = False

        render_bullets(g, p, inventory.inventoryP[inventory.state], client, FPS)
        client.render_enemy_bullets(inventory.inventoryP[inventory.state],g.screen)
        inventory.draw_inventory(g.screen)
        Drone.draw_drone(g.screen,droneB,dronebuttonlist,(t.time()-drone_start))
        fps = fps_font.render(str(int(FPS)), True, (0,0,0))
        g.screen.blit(fps, (1200,10))
    display.flip()
quit()

#testing branch merge


