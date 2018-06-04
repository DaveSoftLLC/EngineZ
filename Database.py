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
class Server
