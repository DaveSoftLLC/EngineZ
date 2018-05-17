from BaseGame import *

bullets = dict()
g = GameMode(server=True)


class PlayerInstance:
    def __init__(self, player, game):
        self.player = player
        self.game = game

    def check_damage(self, bullets):
        Game = self.game
        player = self.player
        for b in bullets:
            px,py = player.pos
            nx = b[0][0] + 10 * cos(radians(b[1]))
            ny = b[0][1] - 10 * sin(radians(b[1]))
            lx, ly = (nx - px + Game.screen.get_width() // 2, ny - py + Game.screen.get_height() // 2)
            interpolate = [(lx + i * cos(radians(b[1])), ly + i * sin(radians(b[1]))) for i in range(10)]
            for ix, iy in interpolate:
                if player.rect.collidepoint((ix, iy)):
                    player.take_damage(10)
                    break

    def take_damage(self, amount):
        player = self.player
        player.health -= amount


class Server:

    def __init__(self, BUFFER_SIZE):
        self.TCP_IP = ''  # ''159.203.163.149'
        self.TCP_PORT = 4545
        self.BUFFER_SIZE = BUFFER_SIZE  # Normally 1024, but we want fast response
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SO_REUSEADDR)
        self.s.bind((self.TCP_IP, self.TCP_PORT))
        self.s.listen(1)
        self.playerDict = {}
        self.running = True
        self.instance = GameMode(server=True)
        self.send_dict = dict()

    def listen(self):
         while self.running:
              print("Before looking")
              conn, addr = self.s.accept()
              print("After looking")
              conn.settimeout(10)
              threading.Thread(target=self.listen_client, args=(conn, addr)).start()

    def listen_client(self, conn, addr):
         print('thread')
         curPlayer = ''
         while self.running:
              try:
                   data = conn.recv(self.BUFFER_SIZE)
                   if data:
                        try:
                             decoded = pickle.loads(data)
                             self.playerDict[decoded.name] = decoded
                             curPlayer = decoded.name
                             conn.send(pickle.dumps(self.playerDict))
                             bullets[curPlayer] = decoded.bullets
                        except Exception as E:
                            print("Error:", E)
                   else:
                        pass
              except Exception as E:
                   del self.playerDict[curPlayer]
                   print('Connection Broken:', E)
                   break
         conn.close()


juniper = Server(BUFFER_SIZE)
threading.Thread(target=juniper.listen).start()
