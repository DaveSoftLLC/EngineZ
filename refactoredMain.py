import glob
from random import randint

from BaseGame import *

guns = []
shotgun = Gun('Shotgun', image.load('Weapons/shellBullet.png'), 10, 6)
guns.append(shotgun)
collision = image.load('Background/rocks+hole.png')
g = GameMode()
sprites = [image.load('Sprites/sprite1.png'), image.load('Sprites/sprite2.png'), image.load('Sprites/sprite3.png')]
newSprites = [[image.load(file) for file in glob.glob('newSprites/shotgun/idle/*.png')],
              [image.load(file) for file in glob.glob('newSprites/shotgun/move/*.png')],
              [image.load(file) for file in glob.glob('newSprites/shotgun/shoot/*.png')]]

print(newSprites)
p = Player(g, '%d' % (randint(1, 100)), (1200, 1200), 10)
client = Client(p, g, TCP_IP, TCP_PORT, newSprites)
print('finished connecting')
threading.Thread(target=client.get_data).start()
print('beginning main loop')
current_gun = guns[0]
while g.running:
    left_click = False
    for e in event.get():
        if e.type == QUIT:
            g.running = False
        if e.type == MOUSEBUTTONDOWN:
            if e.button == 1:
                left_click = True
    m = mouse.get_pressed()
    mx, my = mouse.get_pos()
    p.rotation = int(degrees(atan2((g.screen.get_width()//2-mx),(g.screen.get_height()//2-my))))
    px, py = p.get_pos()
    keys = key.get_pressed()
    #SPRINT
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

    if left_click or (m[0] == 1 and p.gif_counter % 30 == 0):
        p.state = 2
        for a in range(1,current_gun.spread):
            spread = p.rotation+90-(3-a)*6
            p.bullets.append([(px+5*cos(radians(spread)), py-5*sin(radians(spread))), spread])
    client.update_player(p)
    p.update_gif(newSprites)
    g.draw_screen(p)
    p.render_player(newSprites, g)
    client.render_other_players()
    renderBullets(g, p, current_gun)
    client.render_enemy_bullets(current_gun)
    draw.rect(g.screen, (0,255,0), p.get_rect(), 5)
    display.flip()
quit()

#testing branch merge


