from BaseGame import *
import glob
import multiprocessing as mp
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
        self.background = sorted([file for file in glob.glob('frames/*.jpg')])
        self.running = True

    def draw_home(self):
        screen = self.screen
        index = 0
        myClock = time.Clock()
        while self.running:
            for e in event.get():
                if e.type == QUIT:
                    self.running = False
                    break
            myClock.tick(60)
            file = transform.smoothscale(image.load(self.background[index%len(self.background)]).convert(), (1280,800))
            screen.blit(file, (0,0))
            index += 1
            display.flip()
main = Main()
main.draw_home()
quit()
            
            
