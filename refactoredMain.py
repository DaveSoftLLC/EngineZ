import glob
from random import randint

from BaseGame import *
def main(conn, username):
    g = GameMode()

    #Shotgun bullet range
    #Gun reload time
    #Storm show up on minimap


    inventory = Inventory(g.guns)
    dronebuttonlist = [image.load("Background/dronebutton.png"),image.load("Background/dronebuttondark.png")]

    #collision = image.load('Background/rocks+hole.png').convert_alpha()
    #buildingcollision = image.load('Background/buildings.png').convert_alpha()
    def scale_and_load(path, factor):
        img = image.load(path).convert_alpha()

        x, y = img.get_size()
        return transform.smoothscale(img, (int(x/factor), int(y/factor)))
    def get_fps(old_time):
        return int(1/(t.time()-old_time))

    newSprites = [[scale_and_load(file, 3) for file in glob.glob('Sprites/Idle/*.png')],
                  [scale_and_load(file, 3) for file in glob.glob('Sprites/Shoot/*.png')],
                  [scale_and_load(file, 3) for file in glob.glob('Sprites/ShootIdle/*.png')]]

    droneSprite = [[scale_and_load(file, 2) for file in glob.glob('newSprites/drone/*.png')]]
    droneB = False
    p = Player(g, username, (1200, 1200), 10, 'player')
    p.ammo =[100 for i in range(len(g.guns))]
    client = Client(p,0,g, conn, newSprites)
    threading.Thread(target=client.get_data).start()
    drone_start = 31 #Drone can be used first (30 seconds)
    fps_font = font.SysFont('Arial',18)
    g.current_actor = p
    myClock = time.Clock()
    last_fire = 0
    #Mouse Cursor
    reticle = (               #sized 24x24
      "        ........        ",
      "      ..   ..   ..      ",
      "     ..    ..    ..     ",
      "    ..     ..     ..    ",
      "   ..      ..      ..   ",
      "  ..      oooo      ..  ",
      " ..        ..        .. ",
      "..         ..         ..",
      "..         ..         ..",
      "..         ..         ..",
      "..   o    X..X    o   ..",
      ".....o.....XX.....o.....",
      ".....o.....XX.....o.....",
      "..   o    X..X    o   ..",
      "..         ..         ..",
      "..         ..         ..",
      "..         ..         ..",
      " ..        ..        .. ",
      "  ..      oooo      ..  ",
      "   ..      ..      ..   ",
      "    ..     ..     ..    ",
      "     ..    ..    ..     ",
      "      ..   ..   ..      ",
      "        ........        ")#Took me 2 hours
    datatuple,masktuple=cursors.compile(reticle,black='.',white='X',xor='o')#Compile the code
    mouse.set_cursor((24,24),(12,12),datatuple,masktuple)
    while g.running:
        m = mouse.get_pressed()
        mx, my = mouse.get_pos()
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
                if g.droneB == False:
                    if e.button == 1:
                        left_click = True
                    elif e.button == 5: #scroll to move right
                        inventory.switch("RIGHT")
                    elif e.button == 4:#scroll to move left
                        inventory.switch("LEFT")
            elif e.type == KEYDOWN:
                keys = key.get_pressed()
                if keys[K_z]:
                    g.drone_click(g,p,client)
                if keys[K_e] and g.current_actor.type == 'player':
                    #g.weapon_pickup(p,inventory)
                    client.weapon_pickup(inventory)
        m = mouse.get_pressed()
        mx, my = mouse.get_pos()

        keys = key.get_pressed()
        old_time = t.time()
        if 1:
            g.current_actor.rotation = int(degrees(atan2((g.screen.get_width()//2-mx),(g.screen.get_height()//2-my))))
            px, py = g.current_actor.get_pos()
            #SPRINT only for player
            if keys[K_LSHIFT] and m[0] == 1:
                p.speed = 6
                
            elif keys[K_LSHIFT]:
                p.speed = 14
                
                
            else:
                p.speed = 10
                

            #UP
            if keys[K_w] and g.screen.get_height()//2<py-g.current_actor.speed:
                g.current_actor.move('UP', g.background, g.collisionmap,g.buildingmap, FPS)
            #DOWN
            if keys[K_s] and py+g.current_actor.speed<g.background.get_height()-g.screen.get_height()//2:
                g.current_actor.move('DOWN', g.background, g.collisionmap,g.buildingmap, FPS)
            #LEFT
            if keys[K_a] and g.screen.get_width()//2<px-g.current_actor.speed:
                g.current_actor.move('LEFT', g.background, g.collisionmap,g.buildingmap, FPS)
            #RIGHT
            if keys[K_d] and px+g.current_actor.speed<g.background.get_width()-g.screen.get_width()//2:
                g.current_actor.move('RIGHT', g.background, g.collisionmap,g.buildingmap, FPS)

            if g.current_actor.type == 'player' and left_click and (t.time() - last_fire > 0.3 or (inventory.inventoryP[inventory.state].rate >0 and t.time() - last_fire > inventory.inventoryP[inventory.state].rate)):
                last_fire = t.time()
                p.fire(inventory, FPS)
                
            if m[0] == 1 or m[2] ==1:
                p.state = 1
            else:
                p.player_state(inventory)
                


            g.draw_screen(g.current_actor)
            if g.current_actor.type == 'player':
                p.update_gif(newSprites)
                p.render_player(newSprites, g)
                client.render_other_players()
                client.update_player(p)
            else:
                client.render_other_players(newSprites)
                client.update_drone(g.drone)
                g.drone.update_gif(droneSprite)
                g.drone.render_player(droneSprite, g)
                #If time runs out
                if t.time()-g.drone_start >10:
                    client.drone = 0
                    g.current_actor = p
                    g.drone_start = t.time()
                    g.droneB = False
            #g.draw_weapons(g.screen,g.current_actor.pos)
            client.draw_weapons(g.screen,g.current_actor.pos)
            render_bullets(g, p, client, FPS)
            client.render_enemy_bullets(inventory.inventoryP[inventory.state],g.screen)
            inventory.draw_inventory(g.screen,p.ammo)
            Drone.draw_drone(g.screen,g.droneB,dronebuttonlist,(t.time()-g.drone_start))
            fps = fps_font.render(str(int(FPS)), True, (0,0,0))
            g.screen.blit(fps, (1200,10))
        display.flip()
    quit()


    #testing branch merge
    if __name__ == '__main__':
        main(socket.socket())

