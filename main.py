import game
import menu
running = True
main = menu.Main()
mode = 'login'
username = ''
while running:
    if mode == 'login':
        mode, data = main.login_screen()
    elif mode == 'exit':
        running = False
    elif mode == 'game':
        mode, data = game.main(data)
    elif mode == 'menu':
        main = menu.Main(data)
        mode, data = main.draw_home()
quit()
