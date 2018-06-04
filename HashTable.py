
class Row:
    def __init__(self, username, password, high_score):
        self.username = username
        self.values = {'password': password, 'high_score': high_score}
    def __hash__(self):
        return hash(self.username)

class HashTable:
    def __init__(self):
        self.table = [set() for i in range(1000)]
    def insert(self, row_obj):
        hash_value = self.create_hash(row_obj.username)
        pos = hash_value % len(self.table)
        if self.table[pos] == None:
            self.table[pos] = set([row_obj])
        else:
            self.table[pos].add(row_obj)
    def create_hash(self, username):
        return sum([(ord(char)+username.index(char))**2 for char in username[len(username)//2-1:len(username)//2+2]])+len(username)
    def lookup(self, username):
        hash_value = self.create_hash(username)
        pos = hash_value % len(self.table)
        len_of_index = len(self.table[pos])
        if len_of_index == 0:
            raise KeyError('Object not found in hash table')
        elif len_of_index == 1:
            for value in self.table[pos]:
                return value
        else:
            for obj in self.table[pos]:
                if obj.username == username:
                    return obj
if __name__ == '__main__':
    from argon2 import PasswordHasher
    ph = PasswordHasher()
    table = HashTable()
    while True:
        mode = input('Insert or Login: ')
        if mode.lower() == 'insert':
            username = input('Enter a username: ')
            password = ph.hash(input('Enter a password: '))
            obj = Row(username, password, 50)
            table.insert(obj)
        elif mode.lower() == 'login':
            username = input('Enter a username: ')
            password = input('Enter a password: ')
            try:
                obj = table.lookup(username)
                ph.verify(obj.values['password'], password)
                print('Welcome:', username)
            except Exception as E:
                print('Error:', E)
