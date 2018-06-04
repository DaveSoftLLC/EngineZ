from argon2 import PasswordHasher
from HashTable import *
import pickle
from refactoredThreadServer import Server
class Database:
    def __init__(self, file):
        with open(file, 'rb') as file:
            self.table = pickle.load(file)
        self.file = file
    def authenticate(self, conn):
        username, password = pickle.loads(conn.recv(1024))
        try:
            if self.table.lookup(username).values['password'] == password:
                return True
        except KeyError:
            pass
        conn.close()
        return False
    def insert(self, conn):
        username, password = pickle.loads(conn.recv(1024))
        obj = Row(username, password, 0)
        conn.close()
class AuthenticateServer:
    def __init__(self, TCP_IP, TCP_PORT, BUFFER_SIZE):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((TCP_IP, TCP_PORT))
        self.s.listen(1)
        
    
