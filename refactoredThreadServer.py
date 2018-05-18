from BaseGame import *
import multiprocessing as mp
bullets = dict()
g = GameMode(server=True)


class PlayerInstance:
    def __init__(self, player, game):
        self.player = player
        self.game = game

    def check_damage(self, all_bullets):
        g = self.game
        player = self.player
        for b in all_bullets:
            px,py = player.pos
            nx = b[0][0]
            ny = b[0][1]
            lx, ly = (nx - px + g.screen.get_width() // 2, ny - py + g.screen.get_height() // 2)
            for a in range(1, 6):
                angle = b[1] + 90 - (3 - a) * 6
                interpolate = [(lx - i * cos(radians(angle)), ly + i * sin(radians(angle))) for i in range(20)]
                for ix, iy in interpolate:
                    if player.rect.collidepoint((ix, iy)):
                        player.take_damage(10)
                        break

    def take_damage(self, amount):
        player = self.player
        player.health -= amount

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
        self.running = True
        self.instance = GameMode(server=True)
        self.send_dict = dict()
        self.game = game

    def listen(self):
         while self.running:
              print("Before looking")
              conn, addr = self.s.accept()
              print("After looking")
              conn.settimeout(10)
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
                             self.player_dict[decoded.name] = decoded
                             current_player = decoded.name
                             conn.send(pickle.dumps(self.player_dict))
                             bullets[current_player] = decoded.bullets
                        except Exception as E:
                            print("Error:", E)
                   else:
                        pass
              except Exception as E:
                  print(E)

         conn.close()

    def check_damage(self, all_bullets):
        g = self.game
        for b in all_bullets:
            for p in self.player_dict.values():
                px, py = p.pos
                nx = b[0][0]
                ny = b[0][1]
                lx, ly = (nx - px + g.background.get_width() // 2, ny - py
                          + g.background.get_height() // 2)
                for a in range(1, 6):
                    angle = b[1] + 90 - (3 - a) * 6
                    interpolate = [(lx - i * cos(radians(angle)),
                                    ly + i * sin(radians(angle))) for i in range(20)]
                    for ix, iy in interpolate:
                        if p.rect.collidepoint((ix, iy)):
                            p.take_damage(10)
                            break

    def take_damage(self, amount):
        self.player.health -= amount

juniper = Server(g, BUFFER_SIZE)
threading.Thread(target=juniper.listen).start()
while juniper.running:
    try:
        bullet_list = []
        for p in juniper.player_dict:
            bullet_list.append(p.bullets)
        if __name__ == '__main__':
            with mp.Pool(mp.cpu_count()) as p:
                p.map(juniper.check_damage, bullet_list)
    except Exception as E:
        print('Error Checking Bullets:', E)
