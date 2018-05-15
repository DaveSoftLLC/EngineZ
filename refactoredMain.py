from BaseGame import *

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
        if e.type == MOUSEBUTTONDOWN:
            if e.button == 1:
                left_click = True
    mb = mouse.get_pressed()
    mx, my = mouse.get_pos()
    p.rotation = int(degrees(atan2((g.screen.get_width()//2-mx),(g.screen.get_height()//2-my))))
    px, py = p.get_pos()
    keys = key.get_pressed()
    #SPRINT
    if keys[K_LSHIFT] and mb[0] == 1:
        p.speed = 5
        p.state = 2
    elif keys[K_LSHIFT]:
        p.speed = 15
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

#testing branch merge


