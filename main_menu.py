from BaseGame import *
import glob
import multiprocessing as mp
import queue

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
        self.room = {}
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = player_name
        self.running = True
        self.events = queue.Queue()
    def join_room(self, room_name):
        room_name = room_name
        self.s.connect(TCP_IP, TCP_PORT)
        while self.running:
            room_data = {'name':self.name,
                         'room_name':self.room_name,
                         'mode': 'join',
                         'master':False}
            self.s.send(pickle.dumps(room_data))
            data = pickle.loads(self.s.recv(BUFFER_SIZE))
            if not self.events.empty():
                event = self.events.get(block=False)
                if event == 'leave':
                    conn.send('leaving')
                    conn.close()
                    return False, None
                elif type(event) == list and event[0] == 'change_room':
                    room_name = event[1]
            if type(data) == list:
                self.room = data
            elif data == 'game_begin':
                return True, conn
    def create_room(self):
        self.s.connect(TCP_IP, TCP_PORT)
        while self.running:
            room_data = {'name':self.name,
                         'room_name':self.room_name,
                         'master':True}
class Main:
    def __init__(self):
        self.screen = display.set_mode((1280,800))
        self.background = []
        self.running = True
        self.menu_text = ['JOIN', 'CREATE', 'OPTIONS', 'QUIT']
        self.menu_color = {key: (212,175,55) for key in self.menu_text}
        self.menu_buttons = {w: None for w in self.menu_text}
        font.init()
        self.menu_font = font.Font('geonms-font.ttf', 32)
        self.title_font = font.Font('geonms-font.ttf', 72)
        self.client = None
        self.room_data = None
        self.room_name = ''

    def load_images(self, start, end):
        background = transform.smoothscale(image.load('nmsplanet.jpg').convert(), (1280,800))
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
        wallpaper = transform.smoothscale(image.load('nmsplanet.jpg').convert(), (1280, 800))
        self.msg = ''
        while self.running:
            left_click = False
            for e in event.get():
                if e.type == QUIT:
                    self.running = False
                if e.type == MOUSEBUTTONDOWN:
                    left_click = True
                if e.type == KEYDOWN:
                    if e.key == K_BACKSPACE:
                        if len(self.msg) > 0:
                            self.msg = self.msg[:-1]#Delete a character when backspace is pressed
                    elif e.key < 256:
                        self.msg += e.unicode#Add letter to text
            myClock.tick(144)
            file = transform.smoothscale(self.background[index], (1280,800))
            screen.blit(wallpaper, (0,0))
            if mode == 'menu':
                self.screen.blit(title, (self.screen.get_width()//2-title.get_width()//2, 350))
                menu = self.draw_menu(left_click)
##                screen.blit(menu[0], (x, 350))
            else:
                ui = eval(mode_function[mode])(left_click)
            if mode == 'menu' and (menu or change_screen):
                if menu[1]:
                    target_mode = menu
                    mode = target_mode
##                change_screen = True
##                x = self.shift(menu[0], x)
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
##        menu_background = Surface((300,400))
##        menu_background.set_colorkey(0)
##        menu_background.set_alpha(220)
##        AAfilledRoundedRect(menu_background,(0,0,300,400),(53,121,169), radius=0.1)
        mx, my = mouse.get_pos()
        blitted_words = dict()
        text = []
        for word in self.menu_text:
            index = self.menu_text.index(word) + 1
            button = self.render_button(word, self.menu_color[word])
            w, h = button.get_size()
            x = 400
            y = 400+index*25+index*30
            blitted_words[word] = self.screen.blit(button, (x, y))
        changed = None
        response = self.hover(blitted_words, (mx,my), left_click)
        hovered = None
        if response:
            word, state = response
            if state == 'clicked':
                changed = word
            elif state == 'hover':
                hovered = word
        for word in self.menu_text:
            if word == hovered:
                self.menu_color[word] = (255,255,255)
            else:
                self.menu_color[word] = (212,175,55)
        return changed

    def draw_join(self, left_click):
        w, h = self.screen.get_size()
        AAfilledRoundedRect(self.screen,(w//2-700//2,350,700,200),(53,121,169,100), radius=0.05)
        mx, my = mouse.get_pos()
        join_label = self.menu_font.render('JOIN', True, (255,255,255))
        label_text = {'JOIN':(w//2-join_label.get_width()//2, 310),
                      'ENTER ROOM NAME:': (300,375)}
        connect_button = self.render_button('CONNECT', (255,255,255))
        self.screen.blit(connect_button, (w//2-connect_button.get_width()//2, 500))
        for word, pos in label_text.items():
            rendered = self.menu_font.render(word, True, (255,255,255))
            self.screen.blit(rendered, pos)
        box = self.input_box(self.msg, 'geonms-font.ttf', 32, 500, 40)
        bw, bh = box.get_size()
        self.screen.blit(box, (w//2-bw//2, 435))
        return False
    
    def render_room(self, left_click, room_name):
        w, h = self.screen.get_size()
        AAfilledRoundedRect(self.screen,(w//2-700//2,350,700,200),(53,121,169,100), radius=0.05)
        mx, my = mouse.get_pos()
        join_label = self.menu_font.render('JOIN', True, (255,255,255))
        label_text = {'JOIN':(w//2-join_label.get_width()//2, 310),
                      'ENTER ROOM NAME:': (300,375)}
        connect_button = self.render_button('CONNECT', (255,255,255))
        self.screen.blit(connect_button, (w//2-connect_button.get_width()//2, 500))
        room_members = []
        client = ClientMatch('temp')
        
        
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

    def render_button(self, text, box_color):
        render_text = self.menu_font.render(text, True, (0,0,0))
        w, h = render_text.get_size()
        button_surf = Surface((w+24,h+6))
        button_surf.fill(box_color)
        button_surf.blit(render_text, (12,3))
        return button_surf
    
    def hover(self, button_list, mouse_pos, left_click):
        for word, r in button_list.items():
            if r.collidepoint(mouse_pos):
                if left_click:
                    return word, 'clicked'
                return word, 'hover'
        return None

    def input_box(self, msg, font_name, start_size, width, height):
        def justify(text, size):
            newFont = font.Font(font_name, size)
            msg = newFont.render(text, True, (0,0,0))
            newWidth, newHeight = msg.get_size()
            while newWidth > width:
                newWidth = msg.get_width()
                newFont = font.Font(font_name, size)
                msg = newFont.render(text, True, (0,255,0))
                newWidth = msg.get_width()
                size -= 1
            return size
        box = Surface((width, height))
        box.set_colorkey(0)
        input_rect = Rect(0,0,width,height)
        AAfilledRoundedRect(box, input_rect, (255,255,255))
        rendered_msg = font.Font(font_name, justify(msg, start_size)).render(msg, True, (0,0,0))
        box.blit(rendered_msg, (5,0))
        return box
        
main = Main()
main.draw_home()
quit()
            
            
