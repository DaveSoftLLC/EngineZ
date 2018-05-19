import glob
from random import randint

from BaseGame import *

shotgun = Gun('Shotgun', image.load('Weapons/shellBullet.png'), 10,image.load('Weapons/shotgun.png'), 6)
inventory = Inventory(shotgun,shotgun,shotgun,shotgun,shotgun,shotgun)

#inventory.append(shotgun)
inventory.add_item(shotgun)
collision = image.load('Background/rocks+hole.png')
g = GameMode()
sprites = [image.load('Sprites/sprite1.png'), image.load('Sprites/sprite2.png'), image.load('Sprites/sprite3.png')]
newSprites = [[image.load(file).convert_alpha() for file in glob.glob('newSprites/shotgun/idle/*.png')],
              [image.load(file).convert_alpha() for file in glob.glob('newSprites/shotgun/move/*.png')],
              [image.load(file).convert_alpha() for file in glob.glob('newSprites/shotgun/shoot/*.png')]]

droneSprite = [[image.load(file) for file in glob.glob('newSprites/drone/*.png')]]
droneB = False
p = Player(g, '%d' % (randint(1, 100)), (1200, 1200), 10, 'player')
client = Client(p,0,g, '127.0.0.1', 4545, newSprites)
#threading.Thread(target=client.get_data).start()

current_actor = p
while g.running:
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
                if droneB == False:
                    drone = Drone(g, '%s' % ("Drone"), (p.pos), 10, 'drone')
                    current_actor = drone
                    client.drone = drone
                    droneB = True
                else:
                    client.drone = 0
                    current_actor = p
                    droneB = False
    m = mouse.get_pressed()
    mx, my = mouse.get_pos()
    
    keys = key.get_pressed()

    if 1:
        current_actor.rotation = int(degrees(atan2((g.screen.get_width()//2-mx),(g.screen.get_height()//2-my))))
        px, py = current_actor.get_pos()
        #SPRINT
        if keys[K_LSHIFT] and m[0] == 1:
            p.speed = 5
            p.state = 2
        elif keys[K_LSHIFT]:
            p.speed = 15
            p.state = 1
        else:
            p.speed = 10
            p.state = 0

        #UP
        if keys[K_w] and g.screen.get_height()//2<py-current_actor.speed:
            current_actor.move('UP', g.background, g.collisionmap)
        #DOWN
        if keys[K_s] and py+p.speed<g.background.get_height()-g.screen.get_height()//2:
            current_actor.move('DOWN', g.background, g.collisionmap)
        #LEFT
        if keys[K_a] and g.screen.get_width()//2<px-current_actor.speed:
            current_actor.move('LEFT', g.background, g.collisionmap)
        #RIGHT
        if keys[K_d] and px+current_actor.speed<g.background.get_width()-g.screen.get_width()//2:
            current_actor.move('RIGHT', g.background, g.collisionmap)

        if current_actor.type == 'player' and left_click or (m[0] == 1 and p.gif_counter % 30 == 0):
            p.state = 2
            for a in range(1,inventory.inventoryP[inventory.state].spread):
                spread = p.rotation+90-(3-a)*6
                p.bullets.append([(px+5*cos(radians(spread)), py-5*sin(radians(spread))), spread])
            p.fire(inventory)
        g.draw_screen(current_actor)
        if current_actor.type == 'player':
            p.update_gif(newSprites)
            p.render_player(newSprites, g)
            client.render_other_players()
            client.update_player(p)
        else:
            drone.update_gif(droneSprite)
            drone.render_player(droneSprite, g)
            client.render_other_players(newSprites)
            client.update_drone(drone)
        render_bullets(g, p, inventory.inventoryP[inventory.state])
        client.render_enemy_bullets(inventory.inventoryP[inventory.state])
        inventory.draw_inventory(g.screen)
    display.flip()
quit()

#testing branch merge


