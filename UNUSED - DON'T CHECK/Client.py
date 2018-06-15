import pickle
import socket


class Client:
    def __init__(self,player,TCP_IP,TCP_PORT):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player = player
        self.ip = TCP_IP
        self.port = TCP_PORT
    def getData(self,running,otherPlayers):
        self.s.connect((self.TCP_IP,self.TCP_PORT))
        while running:
            p = self.player
            playerList = [p.name,p.pos,p.rotation,p.state,p.health,p.bullets,p.speed]
            binary = pickle.dumps(playerList)
            self.s.send(binary)
            data = pickle.loads(self.s.recv(500))
            otherPlayers = data
        self.s.close()




