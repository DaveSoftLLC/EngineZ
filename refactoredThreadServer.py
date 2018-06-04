from BaseGame import *
import copy
import multiprocessing as mp
del_bullets = dict()
g = GameMode(server=True)

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
        self.instance = GameMode(server=True)
        self.send_dict = dict()
        self.game = game
        self.storm_time  = 30000000000000000
        self.storm_pos = [randint(-100,11500),randint(-100,7500)]
        self.storm_rad = [7000,4000,2500,1000,500,100]
        self.number_threads = 0
        self.stormB = True
        self.storm_state = 0
        assaultrifle = Gun('AR',image.load('Weapons/lightbullet.png'),5,image.load('Weapons/machinegun.png'),0,0.15)
        shotgun = Gun('Shotgun', image.load('Weapons/shellBullet.png'),10,image.load('Weapons/shotgunb.png'), 6,0)
        sniper = Gun('Sniper',image.load('Weapons/heavyBullet.png'),25,image.load('Weapons/sniper.png'),1,0)
        self.weapon_dict = {"Shotgun":shotgun,"AR":assaultrifle,"Sniper":sniper}
        self.weapon_map =[]
        for i in range(20):
            weapon = choice(list(self.weapon_dict))
            wx,wy = (randint(100,11900),randint(100,7900))
            self.weapon_map.append([weapon,(wx,wy),100])
            #self.weapon_map will be sent along with player_dict, client will send weapon that they picked up, and the weapon they will drop (or none)
    def listen(self):
         while self.running:
              print("Before looking")
              conn, addr = self.s.accept()
              print("After looking")
              conn.settimeout(10)
              threading.Thread(target=self.listen_client, args=(conn, addr)).start()
              self.number_threads+=1
              if self.number_threads >0 and self.stormB:
                  self.stormB = False
                  self.storm(True)
              

    def listen_client(self, conn, addr):
        print('thread')
        current_player = ''
        while self.running:
            try:
                data = conn.recv(self.BUFFER_SIZE)
                #print(data)
                if data:
                    try:
                        decoded = pickle.loads(data)
                        current_player = decoded.name
                        self.player_dict[decoded.name] = decoded
                        
                        if current_player not in self.player_health_dict.keys():
                            self.player_health_dict[current_player] = 100
                        else:
                            for key, value in self.player_health_dict.items():
                                self.player_dict[key].health = value
                        #Remove and add weapons
                        #print(self.player_dict[current_player].weapon_send)
                        
                        if len(self.player_dict[current_player].weapon_send) > 0:
                            if len(self.player_dict[current_player].weapon_send) == 1:
                                del self.weapon_map[self.weapon_map.index(self.player_dict[current_player].weapon_send[0])]
                            else:
                                self.weapon_map.append(self.player_dict[current_player].weapon_send[1])
                                del self.weapon_map[self.weapon_map.index(self.player_dict[current_player].weapon_send[0])]
                            self.player_dict[current_player].weapon_send = ["Sent"]
                        self.player_dict[current_player].weapon_map = self.weapon_map
                        if current_player in del_bullets: #Disconnect, bullets will be deleted
                            self.player_dict[current_player].del_bullets += del_bullets[current_player]
                        del_bullets[current_player] = []
                        conn.send(pickle.dumps(self.player_dict))
                        #print("sent")
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
    def storm(self,start = False):
        if start:
            self.storm_time = t.time()
        
        if t.time()-self.storm_time>20:
            print("THE STORM")
juniper = Server(g, BUFFER_SIZE)
threading.Thread(target=juniper.listen).start()
while juniper.running:
    try:
        juniper.check_damage()
        juniper.storm()
    except Exception as E:
        print('Error Checking Bullets:', E)
