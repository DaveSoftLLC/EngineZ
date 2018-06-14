from BaseGame import *
import glob
import multiprocessing as mp
import queue
from argon2 import PasswordHasher
import authenticate

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
        self.name = player_name
        self.running = True
        self.events = queue.Queue()
        self.send_queue = queue.Queue()
    def join_room(self, room_name):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        room_name = room_name
        self.s.connect((TCP_IP, TCP_PORT))
        print('room name', room_name)
        room_data = {'name':self.name,
             'room_name':room_name,
             'ready':False,
             'mode': 'join',
             'master':False}
        self.s.send(pickle.dumps(room_data))
        data = pickle.loads(self.s.recv(BUFFER_SIZE))
        if data != 'all_good':
            self.s.close()
            self.send_queue.put((False, None))
            print('not all good :(')
            return
        ready = False
        fps_clock = time.Clock()
        while self.running:
            fps_clock.tick(50)
            room_data = {'name':self.name,
                         'room_name':room_name,
                         'ready':ready,
                         'mode': 'join',
                         'master':False}
            self.s.send(pickle.dumps(room_data))
            data = pickle.loads(self.s.recv(BUFFER_SIZE))
            print('server:', data)
            self.send_queue.put(data)
            if not self.events.empty():
                event = self.events.get(block=False)
                if event == 'leave':
                    print('leaving')
                    self.s.close()
                    self.send_queue.put((False, None))
                    return
                elif event == 'ready':
                    ready = True
            if type(data) == list:
                self.room = data
            elif data == 'game_begin':
                self.send_queue.put((True, self.s))
                print('begin')
                return
    def create_room(self, room_name):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        room_name = room_name
        self.s.connect((TCP_IP, TCP_PORT))
        print('room name', room_name)
        room_data = {'name':self.name,
             'room_name':room_name,
             'ready':False,
             'mode': 'create',
             'master':True}
        self.s.send(pickle.dumps(room_data))
        data = pickle.loads(self.s.recv(BUFFER_SIZE))
        if data != 'all_good':
            self.s.close()
            self.send_queue.put((False, None))
            print('not all good :(')
            return
        ready = False
        fps_clock = time.Clock()
        while self.running:
            fps_clock.tick(50)
            room_data = {'name':self.name,
                         'room_name':room_name,
                         'ready':ready,
                         'mode': 'join',
                         'master':True}
            self.s.send(pickle.dumps(room_data))
            data = pickle.loads(self.s.recv(BUFFER_SIZE))
            print('server:', data)
            self.send_queue.put(data)
            if not self.events.empty():
                event = self.events.get(block=False)
                if event == 'leave':
                    print('leaving')
                    self.s.close()
                    self.send_queue.put((False, None))
                    return
                elif event == 'ready':
                    ready = True
            if type(data) == list:
                self.room = data
            elif data == 'game_begin':
                self.send_queue.put((True, self.s))
                print('begin')
                return

    def authenticate(self, username, password):
        self.name = username
        return True
        ph = PasswordHasher()
        #username: pay2lose
        #password: abacus
        sql_request = authenticate.MySQLRequest('s03.jamesxu.ca',
                                                'jamesxu',
                                                'enginez123',
                                                'enginez')
        response = sql_request.select('users',username)
        try:
            if ph.verify(response, password):
                self.name = username
                return True
        except Exception as E:
            print(E,"test")
            return False
class Main:
    def __init__(self, auth=False):
        self.screen = display.set_mode((1280,800))
        self.background = []
        self.running = True
        self.menu_text = ['JOIN', 'CREATE', 'OPTIONS', 'QUIT']
        self.function_text = ['room']
        self.menu_color = {key: (212,175,55) for key in self.menu_text}
        font.init()
        self.mode_buttons = {}
        self.menu_font = font.Font('geonms-font.ttf', 32)
        self.title_font = font.Font('geonms-font.ttf', 72)
        self.client = ClientMatch('NULL')
        self.mode = 'menu'
        self.username = 'pay2lose'
##        self.client = ClientMatch('pay2lose')
        self.room_data = []
        self.room_name = ''
        if auth:
            self.username = auth
            self.client.name = self.username

    def login_screen(self):
        background = transform.smoothscale(image.load('nmsplanet.jpg').convert(), (1280,800))
        mode = 'username'
        input_dict = {'username': '', 'password': ''}
        while self.running:
            left_click = False
            for e in event.get():
                if e.type == QUIT:
                    self.running = False
                if e.type == MOUSEBUTTONDOWN:
                    left_click = True
                if e.type == KEYDOWN:
                    if e.key == K_BACKSPACE:
                        if len(input_dict[mode]) > 0:
                            input_dict[mode] = input_dict[mode][:-1]#Delete a character when backspace is pressed
                    elif e.key < 256:
                        input_dict[mode] += e.unicode#Add letter to text
            self.screen.blit(background, (0,0))
            w, h = self.screen.get_size()
            AAfilledRoundedRect(self.screen,(w//2-700//2,350,700,430),(53,121,169,100), radius=0.05)
            mx, my = mouse.get_pos()
            join_label = self.menu_font.render('LOGIN', True, (255,255,255))
            label_text = {'LOGIN':(w//2-join_label.get_width()//2, 310),
                          'USERNAME:': (300,375),
                          'PASSWORD:': (300,550)}
            button_list = [['LOGIN', 'center', 700]]
            click, word = check_hover(self.screen, button_list, self.mode_buttons, (mx,my), left_click, self.menu_font)
            if click:
                if word == 'LOGIN':
                    auth = self.client.authenticate(input_dict['username'], input_dict['password'])
                    if auth:
                        self.username = input_dict['username']
                        return self.draw_home()
            for word, pos in label_text.items():
                rendered = self.menu_font.render(word, True, (255,255,255))
                self.screen.blit(rendered, pos)
            username_box = self.input_box(input_dict['username'], 'geonms-font.ttf', 32, 500, 40)
            password_box = self.input_box('*'*len(input_dict['password']), 'geonms-font.ttf', 32, 500, 40)
            uw, uh = username_box.get_size()
            pw, ph = password_box.get_size()
            rendered_username = self.screen.blit(username_box, (w//2-uw//2, 435))
            rendered_password = self.screen.blit(password_box, (w//2-pw//2, 600))
            if rendered_username.collidepoint((mx,my)) and left_click:
                mode = 'username'
            elif rendered_password.collidepoint((mx,my)) and left_click:
                mode = 'password'
            display.flip()
        return 'exit', 'no_auth'
            

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
        self.load_images(0,15)
        myClock = time.Clock()
        increment = 1
        change_screen = False
        x = 490
        target_mode = ''
        mode_function = {word: str('self.draw_' + word.lower()) for word in self.menu_text + self.function_text}
        title = self.title_font.render('outcast: the game', True, (255,255,255))
        wallpaper = transform.smoothscale(image.load('nmsplanet.jpg').convert(), (1280, 800))
        self.msg = ''
        while self.running:
            left_click = False
            for e in event.get():
                if e.type == QUIT:
                    self.running = False
                    return 'exit', 'None'
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
            if self.mode == 'menu':
                self.screen.blit(title, (self.screen.get_width()//2-title.get_width()//2, 350))
                menu = self.draw_menu(left_click)
                if menu:
                    self.mode = menu
            else:
                ui = eval(mode_function[self.mode])(left_click)
                if ui == "game_begin":
                    return "game", self
            index += increment
            if index == len(self.background) or index == 0:
                increment *= -1
                index += increment
            display.flip()

    def draw_menu(self, left_click):
        mx, my = mouse.get_pos()
        blitted_words = dict()
        text = []
        for word in self.menu_text:
            index = self.menu_text.index(word) + 1
            button = render_button(word, self.menu_color[word], self.menu_font)
            w, h = button.get_size()
            x = 400
            y = 400+index*25+index*30
            blitted_words[word] = self.screen.blit(button, (x, y))
        changed = None
        response = hover(blitted_words, (mx,my), left_click)
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
        button_list = [['CONNECT', 'center', 500], ['BACK', 350, 500]]
        click, word = check_hover(self.screen, button_list, self.mode_buttons, (mx,my), left_click, self.menu_font)
        if click:
            if word == 'BACK':
                self.mode = 'menu'
                self.msg = ''
                self.mode_buttons = {}
            elif word == 'CONNECT':
                self.mode_buttons = {}
                self.room_name = self.msg
                self.mode = 'room'
                threading.Thread(target=self.client.join_room, args=(self.msg,)).start()
                self.msg = ''
                return True
        for word, pos in label_text.items():
            rendered = self.menu_font.render(word, True, (255,255,255))
            self.screen.blit(rendered, pos)
        box = self.input_box(self.msg, 'geonms-font.ttf', 32, 500, 40)
        bw, bh = box.get_size()
        self.screen.blit(box, (w//2-bw//2, 435))
        return False
    
    def draw_room(self, left_click):
        button_list = [['READY', 'center', 720], ['BACK', 350, 720]]
        room_name = self.room_name
        w, h = self.screen.get_size()
        bx, by, bw, bh = AAfilledRoundedRect(self.screen,(w//2-700//2,350,700,430),(53,121,169,100), radius=0.05)
        mx, my = mouse.get_pos()
        join_label = self.menu_font.render('ROOM: {}'.format(room_name), True, (255,255,255))
        label_text = {'ROOM: %s' %room_name:(w//2-join_label.get_width()//2, 310),
                      'PLAYERS:': (300,375)}
        for word, pos in label_text.items():
            self.screen.blit(self.menu_font.render(word, True, (255,255,255)), pos)
        click, word = check_hover(self.screen, button_list, self.mode_buttons, (mx,my), left_click, self.menu_font)
        if not self.client.send_queue.empty():
            data = self.client.send_queue.get(block=False)
            if type(data) == list:
                self.room_data = data
                print(data)
##                screen, rect, username, master, color, font
                for p in range(len(data)):
                    username, status = self.room_data[p]
                    rect = (bx+25,
                            by + 70 + p*60 + p*10,
                            bw-50,
                            60)
                    player_bar(self.screen, rect, username, status, (128,128,128), self.menu_font)
                            
                    
            elif type(data) == tuple:
                print('tuple mode')
                status, conn = data
                if not status:
                    print(data)
                    click = True
                    word = 'BACK'
                elif status:
                    print('starting game')
                    self.running = False
                    return "game_begin"

        if click:
            if word == 'READY':
                self.client.events.put('ready')
            elif word == 'BACK':
                self.client.events.put('leave')
                self.mode = 'JOIN'
                self.mode_buttons = {}
        room_members = []
        client = ClientMatch('temp')
        
        
    def draw_create(self, left_click):
        w, h = self.screen.get_size()
        AAfilledRoundedRect(self.screen,(w//2-700//2,350,700,200),(53,121,169,100), radius=0.05)
        mx, my = mouse.get_pos()
        join_label = self.menu_font.render('CREATE ROOM', True, (255,255,255))
        label_text = {'CREATE ROOM':(w//2-join_label.get_width()//2, 310),
                      'ENTER ROOM NAME:': (300,375)}
        button_list = [['CREATE', 'center', 500], ['BACK', 350, 500]]
        click, word = check_hover(self.screen, button_list, self.mode_buttons, (mx,my), left_click, self.menu_font)
        if click:
            if word == 'BACK':
                self.mode = 'menu'
                self.msg = ''
            elif word == 'CREATE':
                self.mode_buttons = {}
                self.room_name = self.msg
                self.mode = 'room'
                threading.Thread(target=self.client.create_room, args=(self.msg,)).start()
                self.msg = ''
                return True
        for word, pos in label_text.items():
            rendered = self.menu_font.render(word, True, (255,255,255))
            self.screen.blit(rendered, pos)
        box = self.input_box(self.msg, 'geonms-font.ttf', 32, 500, 40)
        bw, bh = box.get_size()
        self.screen.blit(box, (w//2-bw//2, 435))
        return False

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
    def draw_quit(self, left_click):
        self.running = False
        return 'exit', 'None'
    
def render_button(text, box_color, font):
    render_text = font.render(text, True, (0,0,0))
    w, h = render_text.get_size()
    button_surf = Surface((w+24,h+6))
    button_surf.fill(box_color)
    button_surf.blit(render_text, (12,3))
    return button_surf
    
def hover(button_dict, mouse_pos, left_click):
    for word, r in button_dict.items():
        if r.collidepoint(mouse_pos):
            if left_click:
                return word, 'clicked'
            return word, 'hover'
    return None

def check_hover(screen, buttons, button_dict, mouse_pos, left_click, font):
    '''
    [[word, x, y]]
    x = int or x = 'center'
    '''
    w, h = screen.get_size()
    for b in buttons:
        button = render_button(b[0], (212,175,55), font)
        y = b[2]
        if b[1] == 'center':
            x = w//2-button.get_width()//2
        else:
            x = b[1]
        button_dict[b[0]] = [screen.blit(button, (x,y)), (212,175,55)]
    response = hover({key: value[0] for key, value in button_dict.items()}, mouse_pos, left_click)
    hovered = None
    if response:
        word, state = response
        if state == 'clicked':
            return (True, word)
##            if word == 'BACK':
##                self.mode = 'menu'
##            elif word == 'CONNECT':
##                self.room_name = self.msg
##                self.mode = 'room'
##                self.msg = ''
##                return True
        elif state == 'hover':
            hovered = word
    if hovered:
        for word, b in button_dict.items():
            if word == hovered:
                button = render_button(word, (255,255,255), font)
                screen.blit(button, (b[0][0], b[0][1]))
                break
        return (False, hovered)
    return (None, None)

def player_bar(screen, rect, username, master, color, font):
    'screen, rect, username, master, color, font'
    draw.rect(screen, color, rect)
    tx, ty, tw, th = rect
    synonyms = {True: 'Ready', False: 'Waiting'}
    username_rendered = font.render(username, True, (255,255,255))
    status_rendered = font.render(synonyms[master], True, (255,255,255))
    h = username_rendered.get_height()
    screen.blit(username_rendered, (tx+20, ty+th//2-h//2))
    screen.blit(status_rendered, (tx+400, ty+th//2-h//2))
##main = Main()
##main.login_screen()
####main.draw_home()
##import refactoredMain
##s = main.client.s
##username = main.client.name
##main = None
##refactoredMain.main(s, username)
