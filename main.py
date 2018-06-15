import game
import menu
import pygame as pg
import sys
running = True
main = menu.Main()
mode = 'login'
username = ''
while running:
    if mode.lower() == 'login':
        mode, data = main.login_screen()
    elif mode.lower() == 'exit':
        running = False
    elif mode.lower() == 'game':
        mode, data = game.main(data)
    elif mode.lower() == 'menu':
        main = menu.Main(data)
        mode, data = main.draw_home()
pg.quit()
sys.exit()
quit()
