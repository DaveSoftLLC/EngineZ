import socket,pickle
class Client:
    def __init__(self,player,TCP_IP,TCP_PORT):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player = player
    def getData(self,running):
        self.s.connect((TCP_IP,TCP_PORT))
        while running:
            p = self.player
            playerList = [p.name,p.pos,p.rotation,p.state,p.health,p.bullets,p.speed]
            binary = pickle.dumps(self.player)
            self.s.send(binary)
            data = pickle.loads(self.s.recv(500))
            


