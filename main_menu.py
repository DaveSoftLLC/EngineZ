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
        i = 0
        for file in sorted(list(glob.glob('frames/*.jpg')))[:50]:
            self.background.append(image.load(file).convert())
        self.running = True
        self.menu_text = ['JOIN', 'CREATE', 'OPTIONS', 'QUIT']
        self.menu_color = {key: (255,255,255) for key in self.menu_text}
        font.init()
        self.menu_font = font.Font('geonms-font.ttf', 32)
        self.title_font = font.Font('geonms-font.ttf', 72)

    def draw_home(self):
        screen = self.screen
        index = 0
        myClock = time.Clock()
        increment = 1
        while self.running:
            for e in event.get():
                if e.type == QUIT:
                    self.running = False
            myClock.tick(60)
            file = transform.smoothscale(self.background[index], (1280,800))
            screen.blit(file, (0,0))
            self.draw_menu()
            index += increment
            if index == len(self.background) or index == 0:
                increment *= -1
                index += increment
            display.flip()

    def draw_menu(self):
        menu_background = Surface((300,400))
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
        for word, rect in blitted_words.items():
            try:
                if Rect(rect).collidepoint((mx-490, my-350)):
                    self.menu_color[word] = (238,168,73)
                else:
                    self.menu_color[word] = (255,255,255)
            except:
                pass
        self.screen.blit(menu_background, (490,350))
        title = self.title_font.render('OUTCAST: THE GAME', True, (255,255,255))
        self.screen.blit(title, (self.screen.get_width()//2-title.get_width()//2, 125))
        
main = Main()
main.draw_home()
quit()
            
            
