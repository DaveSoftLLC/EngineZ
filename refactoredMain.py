import glob
from random import randint

from BaseGame import *
g = GameMode()
title_font = font.Font('geonms-font.ttf', 72)
menu_font = font.Font('geonms-font.ttf', 32)
background = transform.smoothscale(image.load('nmsplanet.jpg').convert(), (1280,800))
def AAfilledRoundedRect(surface,rect,color,radius=0.4):

    """
    AAfilledRoundedRect(surface,rect,color,radius=0.4)

    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    """

    rect         = Rect(rect)
    color        = Color(*color)
    alpha        = color.a
    color.a      = 0
    pos          = rect.topleft
    rect.topleft = 0,0
    rectangle    = Surface(rect.size,SRCALPHA)

    circle       = Surface([min(rect.size)*3]*2,SRCALPHA)
    draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
    circle       = transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

    radius              = rectangle.blit(circle,(0,0))
    radius.bottomright  = rect.bottomright
    rectangle.blit(circle,radius)
    radius.topright     = rect.topright
    rectangle.blit(circle,radius)
    radius.bottomleft   = rect.bottomleft
    rectangle.blit(circle,radius)

    rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
    rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

    rectangle.fill(color,special_flags=BLEND_RGBA_MAX)
    rectangle.fill((255,255,255,alpha),special_flags=BLEND_RGBA_MIN)

    return surface.blit(rectangle,pos)
def loading_screen(percent, background):
    for e in event.get():
        if e.type == QUIT:
            quit()
    screen = g.screen
    title = title_font.render('outcast: the game', True, (255,255,255))
    msg = menu_font.render('loading', True, (255,255,255))
    width = 500
    height = 25
    main_status_rect = (screen.get_width()//2-width//2,
                        600,
                        width,
                        height)
    progress_rect = (main_status_rect[0],
                     main_status_rect[1], int(percent*500), height)
##        screen.fill(0)
    screen.blit(background, (0,0))
    screen.blit(title, (screen.get_width()//2-title.get_width()//2, 100))
    screen.blit(msg, (screen.get_width()//2-msg.get_width()//2, 550))
    AAfilledRoundedRect(screen, main_status_rect, (255,255,255), 0.4)
    AAfilledRoundedRect(screen, progress_rect, (53,121,169), 0.4)
    display.flip()
    
def main(conn, username):
    inventory = Inventory(g.guns)
    dronebuttonlist = [image.load("Background/dronebutton.png"),image.load("Background/dronebuttondark.png")]

    collision = image.load('Background/rocks+hole.png').convert_alpha()
    image_counter = [0]
    def scale_and_load(path, factor):
        img = image.load(path).convert_alpha()
        x, y = img.get_size()
        
        image_counter[0] += 1
        loading_screen(image_counter[0]//44, background)
        return transform.smoothscale(img, (int(x/factor), int(y/factor)))
    def get_fps(old_time):
        return int(1/(t.time()-old_time))
    sprites = [image.load('Sprites/sprite1.png'), image.load('Sprites/sprite2.png'), image.load('Sprites/sprite3.png')]
    newSprites = [[scale_and_load(file, 3) for file in glob.glob('newSprites/shotgun/idle/*.png')],
                  [scale_and_load(file, 3) for file in glob.glob('newSprites/shotgun/move/*.png')],
                  [scale_and_load(file, 3) for file in glob.glob('newSprites/shotgun/shoot/*.png')]]

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
                    g.weapon_pickup(p,inventory)
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
                p.state = 2
            elif keys[K_LSHIFT]:
                p.speed = 14
                p.state = 1
            else:
                p.speed = 10
                p.state = 0

            #UP
            if keys[K_w] and g.screen.get_height()//2<py-g.current_actor.speed:
                g.current_actor.move('UP', g.background, g.collisionmap, FPS)
            #DOWN
            if keys[K_s] and py+p.speed<g.background.get_height()-g.screen.get_height()//2:
                g.current_actor.move('DOWN', g.background, g.collisionmap, FPS)
            #LEFT
            if keys[K_a] and g.screen.get_width()//2<px-g.current_actor.speed:
                g.current_actor.move('LEFT', g.background, g.collisionmap, FPS)
            #RIGHT
            if keys[K_d] and px+g.current_actor.speed<g.background.get_width()-g.screen.get_width()//2:
                g.current_actor.move('RIGHT', g.background, g.collisionmap, FPS)

            if g.current_actor.type == 'player' and left_click and (t.time() - last_fire > 0.3 or (inventory.inventoryP[inventory.state].rate >0 and t.time() - last_fire > inventory.inventoryP[inventory.state].rate)):
                last_fire = t.time()
                p.state = 2
                p.fire(inventory, FPS)
                
                
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
            g.draw_weapons(g.screen,p.pos)
            render_bullets(g, p, client, FPS)
            client.render_enemy_bullets(inventory.inventoryP[inventory.state],g.screen)
            inventory.draw_inventory(g.screen,p.ammo)
            Drone.draw_drone(g.screen,g.droneB,dronebuttonlist,(t.time()-g.drone_start))
            fps = fps_font.render(str(int(FPS)), True, (0,0,0))
            g.screen.blit(fps, (1200,10))
            if not check_health(p):
                p.die(g.screen)
        display.flip()
    quit()

#testing branch merge
if __name__ == '__main__':
    main(socket.socket(),'james')

