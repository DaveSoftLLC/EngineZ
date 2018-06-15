from BaseGame import *
import glob 
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
        'Class to handle client-side match making'
        self.room = {} #Info of current room
        self.name = player_name #Username
        self.running = True #Flag to keep program running
        self.events = queue.Queue() #Queue to receive data
        self.send_queue = queue.Queue() #Queue to send data
    def join_room(self, room_name):
        'Joins a room'
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Socket object
        room_name = room_name
        self.s.connect((TCP_IP, TCP_PORT)) #Connect to server
        print('room name', room_name)
        room_data = {'name':self.name, #Sends this to server to notify server of these details
             'room_name':room_name,
             'ready':False,
             'mode': 'join',
             'master':False}
        self.s.send(pickle.dumps(room_data))
        data = pickle.loads(self.s.recv(BUFFER_SIZE)) #Receive confirmation from server
        if data != 'all_good':
            self.s.close()
            self.send_queue.put((False, None)) #Send user back to menu if there's an error
            print('not all good :(')
            return
        ready = False #Flag that changes when user clicks ready
        fps_clock = time.Clock() #Limit speed to prevent thread from putting in queue faster than menu code can pull
        while self.running:
            fps_clock.tick(30)
            room_data = {'name':self.name,
                         'room_name':room_name,
                         'ready':ready,
                         'mode': 'join',
                         'master':False} #False, because you didn't create game
            self.s.send(pickle.dumps(room_data))
            data = pickle.loads(self.s.recv(BUFFER_SIZE))
            self.send_queue.put(data)
            if not self.events.empty():
                event = self.events.get(block=False) #Pull from event queue if not empty
                if event == 'leave': #Close socket connection when menu code quits
                    print('leaving')
                    self.s.close()
                    self.send_queue.put((False, None))
                    return
                elif event == 'ready':
                    ready = True #Change ready to reflect user command
            if type(data) == list:
                self.room = data #Update room with data for blitting
            elif data == 'game_begin':
                self.send_queue.put((True, self.s)) #Notify menu code that game is about to begin
                print('begin')
                return
    def create_room(self, room_name):
        'Creates a room for others to join'
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Socket object
        room_name = room_name 
        self.s.connect((TCP_IP, TCP_PORT)) #Connect to server
        print('room name', room_name)
        room_data = {'name':self.name,
             'room_name':room_name,
             'ready':False,
             'mode': 'create',
             'master':True} #Master is true because you are creator
        self.s.send(pickle.dumps(room_data))
        data = pickle.loads(self.s.recv(BUFFER_SIZE))
        if data != 'all_good': #Checks if server confirms room creation
            self.s.close()
            self.send_queue.put((False, None))
            print('not all good :(')
            return
        ready = False
        fps_clock = time.Clock()
        #Rest is same as self.join_room()
        while self.running:
            fps_clock.tick(30)
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
        'Authenticate user based on MySQL database'
        self.name = username
        return True
        ph = PasswordHasher() #Create a passwordhasher object to hash passwords
        #username: pay2lose
        #password: abacus
        sql_request = authenticate.MySQLRequest('s03.jamesxu.ca',
                                                'jamesxu',
                                                'enginez123',
                                                'enginez') #Init database object
        response = sql_request.select('users',username) #Send request
        try:
            if ph.verify(response, password):
                self.name = username #Changes username if successful
                return True
        except Exception as E: #hasher raises an error when passwords don't match
            print(E,"test")
            return False
class Main:
    def __init__(self, auth=False):
        'Class that contains all UI'
        self.screen = display.set_mode((1280,800)) #Screen
        self.background = [] #List of backgrounds to 'simulate' actual loading
        self.running = True #Flag to see if game is running
        self.menu_text = ['JOIN', 'CREATE', 'OPTIONS', 'QUIT'] #Text that needs to be blitted on the home screen
        self.function_text = ['room'] #Non main menu text that still has a corresponding function
        self.menu_color = {key: (212,175,55) for key in self.menu_text} #Colors to keep track for hover
        font.init() #init font system
        self.mode_buttons = {} #Keep track of buttons for hover and click
        self.menu_font = font.Font('geonms-font.ttf', 32) #normal sized font
        self.title_font = font.Font('geonms-font.ttf', 72) #title font
        self.client = ClientMatch('NULL') #init client with NULL username
        self.mode = 'menu' #default mode is main menu
        self.username = 'NULL' #init with NULL username
        self.room_data = [] #Room data for room function starts blank
                            #Remembering old data prevents flickering of blits
        self.room_name = '' #Room name starts blank
        if auth: #This means that the user has already authenticated, for going back to menu from game
            self.username = auth
            self.client.name = self.username

    def login_screen(self):
        'Shows login screen'
        background = transform.smoothscale(image.load('nmsplanet.jpg').convert(), (1280,800)) #Main background
        mode = 'username' #Toggle between username and password
        input_dict = {'username': '', 'password': ''} #Keeps track of entries for both fields
        while self.running:
            left_click = False #Check for a click
            for e in event.get():
                if e.type == QUIT:
                    self.running = False
                if e.type == MOUSEBUTTONDOWN:
                    left_click = True
                if e.type == KEYDOWN:
                    if e.key == K_BACKSPACE:
                        if len(input_dict[mode]) > 0: #only delete if there is at least one character
                            input_dict[mode] = input_dict[mode][:-1]#Delete a character when backspace is pressed
                    elif e.key < 256:
                        input_dict[mode] += e.unicode#Add letter to text
            self.screen.blit(background, (0,0)) #Blit background
            w, h = self.screen.get_size() #width and height of screen
            AAfilledRoundedRect(self.screen,(w//2-700//2,350,700,430),(53,121,169,100), radius=0.05) #draw a rounded rectangle to look nice
            mx, my = mouse.get_pos() #mouse pos
            join_label = self.menu_font.render('LOGIN', True, (255,255,255)) #for login to center the label later
            label_text = {'LOGIN':(w//2-join_label.get_width()//2, 310), #All labels needed to be created with their pos
                          'USERNAME:': (300,375),
                          'PASSWORD:': (300,550)}
            button_list = [['LOGIN', 'center', 700]] #All needed buttons and pos
            click, word = check_hover(self.screen, button_list, self.mode_buttons, (mx,my), left_click, self.menu_font) #check to see if user is clicking or hovering on any button
            if click:
                if word == 'LOGIN':
                    auth = self.client.authenticate(input_dict['username'], input_dict['password'])
                    if auth:
                        self.username = input_dict['username']
                        return self.draw_home() #Draw main menu once user is logged in
            for word, pos in label_text.items():
                #Render and blit at pos
                rendered = self.menu_font.render(word, True, (255,255,255))
                self.screen.blit(rendered, pos)
            username_box = self.input_box(input_dict['username'], 'geonms-font.ttf', 32, 500, 40) #Draw input box
            password_box = self.input_box('*'*len(input_dict['password']), 'geonms-font.ttf', 32, 500, 40) #Draw password box
            uw, uh = username_box.get_size() #width and height for each box
            pw, ph = password_box.get_size()
            rendered_username = self.screen.blit(username_box, (w//2-uw//2, 435)) #Blit each box
            rendered_password = self.screen.blit(password_box, (w//2-pw//2, 600))
            if rendered_username.collidepoint((mx,my)) and left_click: #Change input based on which box is clicked
                mode = 'username' 
            elif rendered_password.collidepoint((mx,my)) and left_click:
                mode = 'password'
            display.flip()
        return 'exit', 'no_auth' #If user leaves now, he has not yet logged in
            

    def load_images(self, start, end):
        'Load images from my GIF frame collection for cool loading bar progress'
        background = transform.smoothscale(image.load('nmsplanet.jpg').convert(), (1280,800)) #Cool wallpaper
        for file in range(start,end):
            #Loop through each file
            self.background.append(image.load("frames/output-{0:06}.jpg".format(file+1)).convert())
            percent = (file-start)/(end-start)
            self.loading_screen(percent, background)
            display.flip()

    def loading_screen(self, percent, background):
        'Draws a loading screen "percent" filled with a background'
        for e in event.get():
            #Allow user to quit
            if e.type == QUIT:
                quit()
        screen = self.screen #Alias for quicker typing
        title = self.title_font.render('outcast: the game', True, (255,255,255)) #Title text
        msg = self.menu_font.render('loading', True, (255,255,255)) #loading text
        width = 500 #width of loading bar
        height = 25 #height
        main_status_rect = (screen.get_width()//2-width//2, #Rect of base bar
                            600,
                            width,
                            height)
        progress_rect = (main_status_rect[0], #Rect of progress bar
                         main_status_rect[1], int(percent*500), height)
##        screen.fill(0)
        screen.blit(background, (0,0))
        screen.blit(title, (screen.get_width()//2-title.get_width()//2, 100))
        screen.blit(msg, (screen.get_width()//2-msg.get_width()//2, 550))
        AAfilledRoundedRect(screen, main_status_rect, (255,255,255), 0.4) #Rounded rects for both base and progress bar
        AAfilledRoundedRect(screen, progress_rect, (53,121,169), 0.4)

    def draw_home(self):
        'Draws main menu home'
        screen = self.screen #Alias
        self.load_images(0,15) #load in images for cool loading screen effect
        myClock = time.Clock() #FPS limiter
        target_mode = ''
        mode_function = {word: str('self.draw_' + word.lower()) for word in self.menu_text + self.function_text} #Dictionary of functions for each mode
        title = self.title_font.render('outcast: the game', True, (255,255,255))
        wallpaper = transform.smoothscale(image.load('nmsplanet.jpg').convert(), (1280, 800)) #wallpaper
        self.msg = '' #Input for joining and creating rooms
        while self.running:
            left_click = False #Flag for mouse click
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
            screen.blit(wallpaper, (0,0))
            if self.mode == 'menu': #menu is special, doesnt appear on the menu buttons list
                self.screen.blit(title, (self.screen.get_width()//2-title.get_width()//2, 350)) #draw in title text
                menu = self.draw_menu(left_click) #draw in the menu
                if menu:
                    self.mode = menu
            else: #for anything else, draws in automatically
                ui = eval(mode_function[self.mode])(left_click)
                if ui == "game_begin": #if game begins, switch to game mode
                    return "game", self
            display.flip()
        return 'exit','None' #Tell launcher to exit game

    def draw_menu(self, left_click):
        'Draw in main menu'
        mx, my = mouse.get_pos() #mouse pos
        blitted_words = dict() #keep track of words that have already been blitted to send to hover function
        for word in self.menu_text:
            #loop through all the menu text and blit them at their respective pos
            index = self.menu_text.index(word) + 1
            button = render_button(word, self.menu_color[word], self.menu_font)
            w, h = button.get_size()
            x = 400
            y = 400+index*25+index*30
            blitted_words[word] = self.screen.blit(button, (x, y))
        changed = None #Mode changed to
        response = hover(blitted_words, (mx,my), left_click) #see if there is any hover/click
        hovered = None
        if response:
            word, state = response
            if state == 'clicked':
                changed = word
            elif state == 'hover':
                hovered = word
        for word in self.menu_text:
            #Change color for the words that have been hovered on
            if word == hovered:
                self.menu_color[word] = (255,255,255)
            else:
                self.menu_color[word] = (212,175,55)
        return changed #return new mode

    def draw_join(self, left_click):
        'Draws in the join screen'
        w, h = self.screen.get_size()
        AAfilledRoundedRect(self.screen,(w//2-700//2,350,700,200),(53,121,169,100), radius=0.05) #Rounded rect to look good
        mx, my = mouse.get_pos()
        join_label = self.menu_font.render('JOIN', True, (255,255,255)) #Same deal as code for login_screen
        label_text = {'JOIN':(w//2-join_label.get_width()//2, 310),
                      'ENTER ROOM NAME:': (300,375)}
        button_list = [['CONNECT', 'center', 500], ['BACK', 350, 500]]#Same deal as code for login_screen
        click, word = check_hover(self.screen, button_list, self.mode_buttons, (mx,my), left_click, self.menu_font)#Same deal as code for login_screen
        if click:#Same deal as code for login_screen
            if word == 'BACK':
                self.mode = 'menu'
                self.msg = ''
                self.mode_buttons = {}
            elif word == 'CONNECT':
                self.mode_buttons = {}
                self.room_name = self.msg #room name is set to typed out message
                self.mode = 'room'
                threading.Thread(target=self.client.join_room, args=(self.msg,)).start() #Begin thread for server connection
                self.msg = '' #Reset to blank
                return True
        for word, pos in label_text.items():
            #Blit each of the lables at their pos
            rendered = self.menu_font.render(word, True, (255,255,255))
            self.screen.blit(rendered, pos)
        box = self.input_box(self.msg, 'geonms-font.ttf', 32, 500, 40) #Input box for entering room name
        bw, bh = box.get_size()
        self.screen.blit(box, (w//2-bw//2, 435))
        return False
    
    def draw_room(self, left_click):
        'Draws in the waiting room'
        button_list = [['READY', 'center', 720], ['BACK', 350, 720]] #Buttons for blitting
        room_name = self.room_name #room name var is set
        w, h = self.screen.get_size()
        bx, by, bw, bh = AAfilledRoundedRect(self.screen,(w//2-700//2,350,700,430),(53,121,169,100), radius=0.05) #Rect values for the nice UI rect
        mx, my = mouse.get_pos()
        join_label = self.menu_font.render('ROOM: {}'.format(room_name), True, (255,255,255)) #Same logic as used in login_screen and many other places
        label_text = {'ROOM: %s' %room_name:(w//2-join_label.get_width()//2, 310),#Same logic as used in login_screen and many other places
                      'PLAYERS:': (300,375)}
        for word, pos in label_text.items():
            self.screen.blit(self.menu_font.render(word, True, (255,255,255)), pos)
        click, word = check_hover(self.screen, button_list, self.mode_buttons, (mx,my), left_click, self.menu_font)
        if not self.client.send_queue.empty():
            #If queue not empty, get from it and set room data equal to new data
            #We store old data to prevent the instance where server sends too slow for client to grab, so it starts flickering or is out of date if we make server connection code too fast
            data = self.client.send_queue.get(block=False)
            self.room_data = data
        if type(self.room_data) == list:
            for p in range(len(self.room_data)):
                #Draw in a nice box for each player in room
                username, status = self.room_data[p]
                rect = (bx+25,
                        by + 70 + p*60 + p*10,
                        bw-50,
                        60)
                player_bar(self.screen, rect, username, status, (128,128,128), self.menu_font)
                
        elif type(self.room_data) == tuple:
            status, conn = self.room_data
            if not status:
                print(self.room_data)
                click = True
                word = 'BACK' #Going back to main menu
            elif status:
                print('starting game') #Start game
                self.running = False
                return "game_begin"

        if click:
            if word == 'READY':
                self.client.events.put('ready') #tell ClientMatch we're ready to start
            elif word == 'BACK':
                #Notify and clear variables of leaving intention
                self.client.events.put('leave')
                self.mode = 'JOIN'
                self.mode_buttons = {}
        
        
    def draw_create(self, left_click):
        'Draw in create room'
        #Same logic as used in draw_join
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
                threading.Thread(target=self.client.create_room, args=(self.msg,)).start() #Slightly different, because after all, we're CREATING a room
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

    def render_button(self, text, box_color):
        'Renders a button'
        render_text = self.menu_font.render(text, True, (0,0,0))
        w, h = render_text.get_size()
        button_surf = Surface((w+24,h+6)) #Slightly padded box
        button_surf.fill(box_color)
        button_surf.blit(render_text, (12,3))
        return button_surf
    
    def hover(self, button_list, mouse_pos, left_click):
        'Checks if a user is clicking on or hovering on a dictionary of buttons'
        for word, r in button_list.items():
            if r.collidepoint(mouse_pos):
                if left_click:
                    return word, 'clicked'
                return word, 'hover'
        return None

    def input_box(self, msg, font_name, start_size, width, height):
        'Box that accepts and displays input'
        def justify(text, size):
            'Continually reduce text size until it fits in box'
            newFont = font.Font(font_name, size) #Init newFont on default params
            msg = newFont.render(text, True, (0,0,0))
            newWidth, newHeight = msg.get_size()
            while newWidth > width:
                #Keep reducing size by 1 until it fits
                newWidth = msg.get_width()
                newFont = font.Font(font_name, size)
                msg = newFont.render(text, True, (0,255,0))
                newWidth = msg.get_width()
                size -= 1
            return size
        box = Surface((width, height)) #New surface
        box.set_colorkey(0) #To make black transparent
        input_rect = Rect(0,0,width,height) #Size of input rect
        AAfilledRoundedRect(box, input_rect, (255,255,255)) #Render the input box
        rendered_msg = font.Font(font_name, justify(msg, start_size)).render(msg, True, (0,0,0)) #draw in the font
        box.blit(rendered_msg, (5,0))
        return box
    def draw_quit(self, left_click):
        'Quits menu'
        self.running = False
        return 'exit', 'None'
    
def render_button(text, box_color, font):
    'Renders a button'
    render_text = font.render(text, True, (0,0,0))
    w, h = render_text.get_size()
    button_surf = Surface((w+24,h+6))
    button_surf.fill(box_color)
    button_surf.blit(render_text, (12,3))
    return button_surf
    
def hover(button_list, mouse_pos, left_click):
    'Checks if a user is clicking on or hovering on a dictionary of buttons'
    for word, r in button_list.items():
        if r.collidepoint(mouse_pos):
            if left_click:
                return word, 'clicked'
            return word, 'hover'
    return None

def check_hover(screen, buttons, button_dict, mouse_pos, left_click, font):
    '''
    Checks hover and renders at the same time
    [[word, x, y]]
    x = int or x = 'center'
    '''
    w, h = screen.get_size()
    for b in buttons:
        button = render_button(b[0], (212,175,55), font) #Renders
        y = b[2] #y position of button
        if b[1] == 'center':
            #Blits in center if center pos is requested
            x = w//2-button.get_width()//2
        else:
            x = b[1] #Otherwise, use given x pos
        button_dict[b[0]] = [screen.blit(button, (x,y)), (212,175,55)] #Update button_dict with latest
    response = hover({key: value[0] for key, value in button_dict.items()}, mouse_pos, left_click) #Check hover for each of the buttons
    hovered = None
    if response:
        word, state = response
        if state == 'clicked':
            return (True, word)
        elif state == 'hover':
            hovered = word
    if hovered: #Reblit each of them with new color
        for word, b in button_dict.items():
            if word == hovered:
                button = render_button(word, (255,255,255), font)
                screen.blit(button, (b[0][0], b[0][1]))
                break
        return (False, hovered) #Return word that was hovered
    return (None, None) #Return None if nothiing happened

def player_bar(screen, rect, username, master, color, font):
    #Bar containing player info
    'screen, rect, username, master, color, font'
    draw.rect(screen, color, rect)
    tx, ty, tw, th = rect #rect sizes
    synonyms = {True: 'Ready', False: 'Waiting'} #maps true and false to words
    username_rendered = font.render(username, True, (255,255,255))
    status_rendered = font.render(synonyms[master], True, (255,255,255))
    h = username_rendered.get_height()
    screen.blit(username_rendered, (tx+20, ty+th//2-h//2)) #blit in middle
    screen.blit(status_rendered, (tx+400, ty+th//2-h//2)) #blit in middle
##main = Main()
##main.login_screen()
####main.draw_home()
##import refactoredMain
##s = main.client.s
##username = main.client.name
##main = None
##refactoredMain.main(s, username)
