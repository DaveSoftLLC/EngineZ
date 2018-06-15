#James Xu and Zhehai Zhang
#Outcast: The Game
#Game Launcher
import game
import menu
import pygame as pg
import sys
running = True #Main flag to determine running
main = menu.Main() #Menu object
mode = 'login' #Used to select and transfer between modes
username = '' #Remembers username when user has logged in already
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
