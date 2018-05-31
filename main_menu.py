from BaseGame import *

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
