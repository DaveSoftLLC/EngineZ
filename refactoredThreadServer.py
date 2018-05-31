from BaseGame import *
import copy
import multiprocessing as mp
del_bullets = dict()


class Room:
    
    def __init__(self, name, clients):
        'name: str; clients = [(conn,addr)]'
        self.player_dict = {}
        self.player_health_dict = {}
        self.running = True
        self.send_dict = dict()
        self.clients = clients
        self.game = GameMode(server=True)

    def create_thread(self):
        for c, a in self.clients:
            threading.Thread(target=self.listen_client, args=(c, a)).start()
        
    def listen_client(self, conn, addr):
        print('thread')
        current_player = ''
        while self.running:
            try:
                data = conn.recv(self.BUFFER_SIZE)
                if data:
                    try:
                        decoded = pickle.loads(data)
                        current_player = decoded.name
                        self.player_dict[decoded.name] = decoded
                        if current_player not in self.player_health_dict.keys():
                            self.player_health_dict[decoded.name] = 100
                        else:
                            for key, value in self.player_health_dict.items():
                                self.player_dict[key].health = value
                        if current_player in del_bullets: #Disconnect, bullets will be deleted
                            self.player_dict[current_player].del_bullets += del_bullets[current_player]
                        del_bullets[current_player] = []
                        conn.send(pickle.dumps(self.player_dict))
                    except Exception as E:
                            print("Error:", E)
                else:
                    pass
            except Exception as E:
                print(E)
                self.remove(current_player)
                break
        conn.close()
        


class Server:
    def __init__(self, game, BUFFER_SIZE):
        self.TCP_IP = ''  # ''159.203.163.149'
        self.TCP_PORT = 4545
        self.BUFFER_SIZE = BUFFER_SIZE  # Normally 1024, but we want fast response
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.TCP_IP, self.TCP_PORT))
        self.s.listen(1)
        self.player_dict = {}
        self.player_health_dict = {}
        self.running = True
        self.send_dict = dict()
        self.game = GameMode(server=True)

    def listen(self):
         while self.running:
              print("Before looking")
              conn, addr = self.s.accept()
              print("After looking")
              conn.settimeout(10)
              data = pickle.loads(conn.recv())
              STRUCT = ['room name', 'player list']
              threading.Thread(target=self.listen_client, args=(conn, addr)).start()

    def listen_client(self, conn, addr):
        print('thread')
        current_player = ''
        while self.running:
            try:
                data = conn.recv(self.BUFFER_SIZE)
                if data:
                    try:
                        decoded = pickle.loads(data)
                        current_player = decoded.name
                        self.player_dict[decoded.name] = decoded
                        if current_player not in self.player_health_dict.keys():
                            self.player_health_dict[decoded.name] = 100
                        else:
                            for key, value in self.player_health_dict.items():
                                self.player_dict[key].health = value
                        if current_player in del_bullets: #Disconnect, bullets will be deleted
                            self.player_dict[current_player].del_bullets += del_bullets[current_player]
                        del_bullets[current_player] = []
                        conn.send(pickle.dumps(self.player_dict))
                    except Exception as E:
                            print("Error:", E)
                else:
                    pass
            except Exception as E:
                print(E)
                self.remove(current_player)
                break
        conn.close()

    def check_damage(self):
        g = self.game
        for name, obj in {k: v for k,v in self.player_dict.items()}.items():
            for b in obj.bullets:
                for p in [i for i in self.player_dict.values()]:
                    if name == p.name:
                        continue
                    if name in del_bullets.keys():
                        if b in del_bullets[name]:
                            continue
                    px, py = p.pos
                    nx = b[0][0]
                    ny = b[0][1]
                    if hypot(px-nx, py-ny) > 60:
                        continue
##                    lx, ly = (nx - px + 1280 // 2, ny - py
##                              + 800 // 2)
                    angle = b[1]
                    interpolate = [(nx - i * cos(radians(angle)),
                                    ny + i * sin(radians(angle))) for i in range(b[3])]
                    counter = 0
                    for ix, iy in interpolate:
                        if hypot(px - nx, py - ny) < 30:
                            counter += 1
                            print(counter, name)
                            obj.bullets.remove(b)
                            if name not in del_bullets.keys():
                                del_bullets[name] = [b]
                            else:
                                del_bullets[name].append(b)
                            if self.player_health_dict[p.name] - 10 >= 0:
                                self.player_health_dict[p.name] -= 10
                            break

    def take_damage(self, amount):
        self.player.health -= amount

    def remove(self, player_name):
        try:
            del self.player_health_dict[player_name]
        except ValueError:
            pass
        try:
            del self.player_dict[player_name]
        except ValueError:
            pass
        try:
            del del_bullets[player_name]
        except ValueError:
            pass
juniper = Server(g, BUFFER_SIZE)
threading.Thread(target=juniper.listen).start()
while juniper.running:
    try:
        juniper.check_damage()
    except Exception as E:
        print('Error Checking Bullets:', E)
