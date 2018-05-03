import socket
class Client:
    def __init__(self,running,player,TCP_IP,TCP_PORT):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((TCP_IP,TCP_PORT))

