from BaseGame import *
import copy
import multiprocessing as mp
import authenticate
del_bullets = dict() #Bullets that the clients need to delete
g = GameMode(server=True) #init a game instance
serverRequest = authenticate.MySQLRequest('s03.jamesxu.ca','jamesxu','enginez123','enginez') #init mysql system

class GameInstance:
    def __init__(self, name, clients):
        '''name: str; clients = [(conn,addr)]
           Server side game logic'''
        self.game_end = False #flag to check to see if game has ended
        self.player_dict = {} #Dictionary of all players and player instances
        self.player_health_dict = {} #Dictionary of health to force reset to prevent cheating
        self.running = True #flag for game running
        self.instance = GameMode(server=True) #init unique instance for each game
        print("finish loading images")
        self.send_dict = dict() #other data to be sent
        self.game = self.instance #alias to be backwards compatible with zhehais code
        self.clients = clients #list of client sockets
        #Gun sprites------------------------------------------------------------------------------------------------
        assaultrifle = Gun('AR',image.load('Weapons/lightbullet.png'),5,image.load('Weapons/machinegun.png'),0,0.15)
        shotgun = Gun('Shotgun', image.load('Weapons/shellBullet.png'),5,image.load('Weapons/shotgunb.png'), 6,0)
        sniper = Gun('Sniper',image.load('Weapons/heavyBullet.png'),25,image.load('Weapons/sniper.png'),1,0)
        rpg = Gun('RPG',image.load('Weapons/rocketammo.png'),20,image.load('Weapons/rpg.png'),1,0)
        self.weapon_dict = {"Shotgun":shotgun,"AR":assaultrifle,"Sniper":sniper,"RPG":rpg}
        self.weapon_map =[]
        #-----------------------------------------------------------------------------------------------------------
        
        for i in range(20):
            #randomly generate 20 weapons
            weapon = choice(list(self.weapon_dict))
            wx,wy = (randint(100,11900),randint(100,7900))
            self.weapon_map.append([weapon,(wx,wy),100])
            #self.weapon_map will be sent along with player_dict, client will send weapon that they picked up, and the weapon they will drop (or none)
        #Storm
        self.storm_time  = 30000000000000000 #Tim
        self.storm_moving  = 6000000000000
        self.storm_next = "idle"
        self.storm_pos = []
        self.storm_rad = [6000,4000,3000,2000,1000,500]
        self.dam = 0
        self.stormB = True
        self.storm_state = 0
        self.storm(True)
        for a in range(len(self.storm_rad)):
            if self.storm_rad[a] == 6000:
                self.storm_pos.append([6000,4000])
            else:
                x = randint(self.storm_pos[a-1][0]-(self.storm_rad[a-1]-self.storm_rad[a])+200,self.storm_pos[a-1][0]+(self.storm_rad[a-1]-self.storm_rad[a])-200)
                y = randint(self.storm_pos[a-1][1]-(self.storm_rad[a-1]-self.storm_rad[a])+200,self.storm_pos[a-1][1]+(self.storm_rad[a-1]-self.storm_rad[a])-200)
                self.storm_pos.append([x,y])
        #start server processing logic
        threading.Thread(target=self.check_damage).start()
        threading.Thread(target=self.storm).start()
        threading.Thread(target=self.check_win).start()
    def create_thread(self):
        'Create listening thread for each player'
        for c in self.clients:
            conn, addr = (c[2], c[3])
            threading.Thread(target=self.listen_client, args=(conn, addr)).start()
            print("create thread")
    def listen_client(self, conn, addr):
        'Listens to each of the clients and handles data transfers'
        print('listen client')
        current_player = '' #username
        running = True #Kills loop if this player dies
        while self.running and running:
            try:
                data = conn.recv(BUFFER_SIZE) #Receive data
                if data == pickle.dumps('leave'):
                    print(current_player, 'is leaving')
                    self.remove(current_player)
                    running = False
                if data:
                    try:
                        decoded = pickle.loads(data) #Decode data
                        current_player = decoded.name
                        self.player_dict[decoded.name] = decoded
                        
                        if current_player not in self.player_health_dict.keys(): #if entry doesnt exist, create it
                            self.player_health_dict[current_player] = 100
                        else:
                            for key, value in self.player_health_dict.items():#otherwise replace player health with server side health
                                self.player_dict[key].health = value
                        #Remove and add weapons
                        #print(self.player_dict[current_player].weapon_send)
                        
                        if len(self.player_dict[current_player].weapon_send) > 0:
                            if self.player_dict[current_player].weapon_send[1] == 0:#Picking up weapon
                                del self.weapon_map[self.weapon_map.index(self.player_dict[current_player].weapon_send[0])]
                            elif self.player_dict[current_player].weapon_send[0] == 0:#dropping weapon
                                self.weapon_map.append(self.player_dict[current_player].weapon_send[1])
                            else:#Picking up and dropping
                                self.weapon_map.append(self.player_dict[current_player].weapon_send[1])
                                del self.weapon_map[self.weapon_map.index(self.player_dict[current_player].weapon_send[0])]
                            self.player_dict[current_player].weapon_send = ["Sent"]
                        if (self.storm_state+1) != len(self.storm_rad):
                            self.player_dict[current_player].storm = [self.storm_pos[self.storm_state],self.storm_rad[self.storm_state],self.storm_next,self.storm_pos[self.storm_state+1],self.storm_rad[self.storm_state+1]]
                        else:
                            self.player_dict[current_player].storm = [self.storm_pos[self.storm_state],self.storm_rad[self.storm_state],self.storm_next]
                                
                        self.player_dict[current_player].weapon_map = self.weapon_map
                        if current_player in del_bullets:
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

    def check_win(self):
        'Check win condition'
        done = False
        while not done: #Only begin when all players have connected
            if len(self.clients) == len(self.player_dict.keys()):
                done = True
        print("begin check_win\n")
        while self.running:
            if len(self.player_dict.keys()) == 1:#Check if there is only one player left
                self.running = False
                player = list(self.player_dict.values())[0].name
                for p in self.clients:
                    if p[0] == player:
                        p[2].send(pickle.dumps('winner'))#Tell them they're the winner
                threading.Thread(target=serverRequest.modify, args=(player, 25)).start() #Give them bonus points
                self.running = False#End game
                self.game_end = True#End game

    def check_damage(self):
        'Check Damage for all players'
        while self.running:
            g = self.game
            name = list(self.player_dict.keys())
            obj = list(self.player_dict.values())
            players = dict(zip(name,obj))
            for name, obj in players.items(): #Loop through each player
                try:
                    x = self.storm_pos[self.storm_state][0]-obj.pos[0]
                    y = self.storm_pos[self.storm_state][1]-obj.pos[1] 
                    if hypot(x,y)>self.storm_rad[self.storm_state] and t.time()-self.dam>1:
                        self.dam = t.time()
                        if self.player_health_dict[name] - 1 >= 0:
                            self.player_health_dict[name] -= 1
                except:
                    pass
                        #print("OUTSIDE STORM")
                for b in obj.bullets: #Loop through each of their bullets
                    for p in [i for i in self.player_dict.values()]: #Loop through the other players
                        if name == p.name: #Skip if its the same player
                            continue
                        if name in del_bullets.keys(): #Make sure it wasnt marked for deletion
                            if b in del_bullets[name]:
                                continue
                        px, py = p.pos #Player pos
                        nx = b[0][0]#Bullet pos
                        ny = b[0][1]
                        if hypot(px-nx, py-ny) > 60: #Skip granular checking if its not even close
                            continue
                        angle = b[1]
                        interpolate = [(nx - i * cos(radians(angle)),
                                        ny + i * sin(radians(angle))) for i in range(b[3])] #Interpolate gaps between each +20ish on pos
##                        interpolate = gameMath.interpolate(int(nx),int(ny),int(angle),int(b[3]))
                        for ix, iy in interpolate: #Loop through interpolated pixels
                            if (b[2] == 'rpg' and hypot(px- nx, py - ny)<60) or hypot(px - nx, py - ny) < 30: #Check if bullet roughly hits player
                                threading.Thread(target=serverRequest.modify, args=(name, 1)).start()#Add points for each hit
                                obj.bullets.remove(b)#Delete bullet so it isnt touched again
                                if name not in del_bullets.keys():
                                    del_bullets[name] = [b]#Add this bullet to del bullets if player isnt in del bulets
                                else:#If already in, append it instead
                                    del_bullets[name].append(b)
                                if self.player_health_dict[p.name] - self.weapon_dict[b[2]].damage > 0: #Take away health
                                    self.player_health_dict[p.name] -= self.weapon_dict[b[2]].damage
##                                elif self.player_health_dict[p.name]<10:
##                                    self.player_health_dict[p.name] = 0
                                else:
                                    threading.Thread(target=serverRequest.modify, args=(name, 5)).start()#If kill, add more points
                                    self.player_health_dict[p.name] = 0
                                break

    def take_damage(self, amount):
        'Takes Damage'
        self.player.health -= amount

    def remove(self, player_name):
        'Tries its best to remove as much as it can from server'
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
        else:
            while self.running:
                if t.time()-self.storm_time>60:
                    self.storm_time = t.time()
                    if self.storm_next == "idle":
                        self.storm_next = "moving"
                        self.storm_rad[self.storm_state]
                        self.x = ((self.storm_pos[self.storm_state+1][0]-self.storm_pos[self.storm_state][0])/(600))
                        self.y = ((self.storm_pos[self.storm_state+1][1]-self.storm_pos[self.storm_state][1])/(600))
                        print(self.x, self.y)
                        print(self.storm_pos)
                        self.r = ((self.storm_rad[self.storm_state]-self.storm_rad[self.storm_state+1])/600)
                        print(self.r)
                        self.storm_moving = 0
                    
                    else:
                        self.storm_next = "idle"
                        if self.storm_state+2 != len(self.storm_rad):
                            self.storm_state += 1
                        else:
                            print("storm iz done")
                            break
                    
                    print("THE STORM")
                if t.time()-self.storm_moving>.1 and self.storm_next == "moving":
                    self.storm_moving = t.time()
                    if (self.storm_state+1) != len(self.storm_rad) and self.storm_rad[self.storm_state] >= self.storm_rad[self.storm_state+1]:
                        self.storm_pos[self.storm_state][0]+=self.x
                        self.storm_pos[self.storm_state][1]+=self.y
                        self.storm_rad[self.storm_state]-= self.r
                        #print(self.storm_rad,self.storm_pos)
                        #print("moving")


class Server:
    def __init__(self, BUFFER_SIZE):
        'Matchmaking Server'
        self.TCP_IP = ''  # ''159.203.163.149' IPADDRESS
        self.TCP_PORT = 4545 #PORT NO.
        self.BUFFER_SIZE = BUFFER_SIZE #Buffer size for sockets
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket object
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #allow it to be reused to avoid weird errors
        self.s.bind((self.TCP_IP, self.TCP_PORT))
        self.s.listen(1)
        self.rooms = {} #Dictionary of all rooms
        self.game = GameMode(server=True) #Game instance
        self.game_instances = {} #Dict of game instances
        self.running = True

    def clean(self):
        fpsClock = time.Clock() 
        while self.running:
            fpsClock.tick(2)#run slowly to avoid CPU hogging
            rooms = dict(zip(list(self.rooms.keys()),list(self.rooms.values())))
            games = dict(zip(list(self.game_instances.keys()),list(self.game_instances.values()))) #zip it all up to prevent size change during iter errors
            for room in rooms.keys():
                if len(self.rooms[room]) == 0:
                    print(room, self.rooms)
                    del self.rooms[room]
            for game, obj in games.items():
                if obj.game_end:
                    del self.game_instances[game]
    
    def listen(self):
        'Listen for connections'
         while self.running:
              print("Before looking")
              conn, addr = self.s.accept()
              print("After looking")
              conn.settimeout(180)
              STRUCT = ['room name', 'player list']
              threading.Thread(target=self.listen_client, args=(conn, addr)).start()#handoff to function for the rest

    def listen_client(self, conn, addr):
        'Handles logic'
        print('room thread')
        data = pickle.loads(conn.recv(self.BUFFER_SIZE))
        name = data['name']#username
        mode = data['mode']#join or create
        room_name = data['room_name']
        if mode == 'join':
            if room_name not in self.rooms.keys():
                conn.send(pickle.dumps('no_such_room'))
                #print(self.rooms.keys(), room_name)
                conn.close()
                return
            elif len(self.rooms[room_name]) >= 5: #max players is 5
                conn.send(pickle.dumps('no_such_room'))
                #print(self.rooms.keys(), room_name)
                conn.close()
                return
        elif mode == 'create':
            if room_name in self.rooms.keys() or room_name in self.game_instances.keys():
                conn.send(pickle.dumps('room_exists'))
                conn.close()
                return
            else:
                self.rooms[room_name] = [[data['name'],data['ready'],conn,addr]]#this is to prevent deletion by clean function
        conn.send(pickle.dumps('all_good'))
        while self.running:
            try:
                data = pickle.loads(conn.recv(self.BUFFER_SIZE))
                name = data['name']
                master = data['master']#creator of room
                room_name = data['room_name']
                ready = data['ready']
                existing = False
                for p in self.rooms[room_name]:
                    if p[0] == name: #update player
                        existing = True
                        p[1] = ready
                        break
                else:
                    self.rooms[room_name].append([name, ready, conn, addr]) #append if player not already in
                start = all([r[1] for r in self.rooms[room_name]]) #everyone clicked ready
                #print(start)
                if start:
                    msg = 'game_begin'
                    conn.send(pickle.dumps(msg))
                    print(self.game_instances.keys())
                    if master:#only run instance creation if you are creator
                        print('room not in game_instances\n')
                        instance = GameInstance(room_name, self.rooms[room_name])
                        self.game_instances[room_name] = instance
                        threading.Thread(target=instance.create_thread).start()
                    return True
                else:
                    players = []#list to send
                    for player in self.rooms[room_name]:
                        players.append(player[:2])
                    msg = pickle.dumps(players)
                    conn.send(msg)
            except Exception as E:
                print(E)
                for player in self.rooms[room_name]:
                    if player[0] == name:
                        self.rooms[room_name].remove(player)#Try and delete from rooms
                        return
        conn.close()

    def remove(self, room):
        'Removes room'
        try:
            del self.rooms[room]
        except:
            print('Room Not found: %s' %room)
if __name__ == '__main__':
    server = Server(BUFFER_SIZE)
    threading.Thread(target=server.listen).start()
    threading.Thread(target=server.clean).start()
