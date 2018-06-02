from BaseGame import *
import glob
import multiprocessing as mp

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


class ClientMatch:
    def __init__(self, player_name):
        self.rooms = {}
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = player_name
        self.room_name = None
        
    def process_rooms(self):
        self.s.connect(TCP_IP, TCP_PORT)
        while True:
            room_data = {'name':self.name,
                         'room_name':self.room_name,
                         'master':False}
            self.s.send(pickle.dumps(room_data))
            data = pickle.loads(self.s.recv(BUFFER_SIZE))
            if data != 'game_begin':
                self.rooms = data
            else:
                break
        return True
class Main:
    def __init__(self):
        self.screen = display.set_mode((1280,800))
        self.background = []
        self.running = True
        self.menu_text = ['JOIN', 'CREATE', 'OPTIONS', 'QUIT']
        self.menu_color = {key: (255,255,255) for key in self.menu_text}
        font.init()
        self.menu_font = font.Font('geonms-font.ttf', 32)
        self.title_font = font.Font('geonms-font.ttf', 72)

    def load_images(self, start, end):
        background = transform.smoothscale(image.load('nmsdark.jpg').convert(), (1280,800))
        for file in range(start,end):
            self.background.append(image.load("frames/output-{0:06}.jpg".format(file+1)).convert())
            percent = (file-start)/(end-start)
            self.loading_screen(percent, background)
            display.flip()

    def loading_screen(self, percent, background):
        for e in event.get():
            if e.type == QUIT:
                quit()
        screen = self.screen
        title = self.title_font.render('outcast: the game', True, (255,255,255))
        msg = self.menu_font.render('loading', True, (255,255,255))
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

    def draw_home(self):
        screen = self.screen
        index = 0
        self.load_images(800,810)
        myClock = time.Clock()
        increment = 1
        change_screen = False
        x = 490
        mode = 'menu'
        target_mode = ''
        mode_function = {word: str('self.draw_' + word.lower()) for word in self.menu_text if word != 'QUIT'}
        title = self.title_font.render('outcast: the game', True, (255,255,255))
        while self.running:
            left_click = False
            for e in event.get():
                if e.type == QUIT:
                    self.running = False
                if e.type == MOUSEBUTTONDOWN:
                    left_click = True
            myClock.tick(60)
            file = transform.smoothscale(self.background[index], (1280,800))
            screen.blit(file, (0,0))
            if mode == 'menu':
                menu = self.draw_menu(left_click)
                screen.blit(menu[0], (x, 350))
            else:
                ui = eval(mode_function[mode])(left_click)
                screen.blit(ui, (490, 350))
            self.screen.blit(title, (self.screen.get_width()//2-title.get_width()//2, 100))
            if mode == 'menu' and (menu[1] or change_screen):
                if menu[1]:
                    target_mode = menu[1]
                change_screen = True
                x = self.shift(menu[0], x)
                if not x:
                    x = 490
                    change_screen = False
                    mode = target_mode
                    target_mode = ''
            index += increment
            if index == len(self.background) or index == 0:
                increment *= -1
                index += increment
            display.flip()

    def draw_menu(self, left_click):
        menu_background = Surface((300,400))
        menu_background.set_colorkey(0)
        menu_background.set_alpha(220)
        AAfilledRoundedRect(menu_background,(0,0,300,400),(53,121,169), radius=0.1)
        mx, my = mouse.get_pos()
        blitted_words = dict()
        text = []
        for w in self.menu_text:
            word = self.menu_font.render(w,True,self.menu_color[w])
            index = self.menu_text.index(w) + 1
            x = menu_background.get_width()//2-word.get_width()//2
            y = index*75
            blitted_words[w] = tuple(menu_background.blit(word, (x, y)))
        changed = None
        for word, rect in blitted_words.items():
            try:
                if Rect(rect).collidepoint((mx-490, my-350)):
                    self.menu_color[word] = (238,168,73)
                    if left_click:
                        changed = word
                    break
                
                else:
                    self.menu_color[word] = (255,255,255)
            except:
                pass        

        return menu_background,changed

    def draw_join(self, left_click):
        join_background = Surface((300,400))
        join_background.set_colorkey(0)
        join_background.set_alpha(220)
        AAfilledRoundedRect(join_background,(0,0,300,400),(53,121,169), radius=0.1)
        mx, my = mouse.get_pos()
        join_label = self.menu_font.render('JOIN', True, (255,255,255))
        join_background.blit(join_label, (join_background.get_width()//2-join_label.get_width()//2,
                                          25))
        return join_background

    def draw_create(self):
        pass

    def draw_options(self):
        pass
        
    def shift(self, surface, original_pos):
        w, h = surface.get_size()
        ox = original_pos
        if ox + w - 30 < 0:
            return False
        return ox - 30
main = Main()
main.draw_home()
quit()
            
            
