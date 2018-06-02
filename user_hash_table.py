class Row:
    def __init__(self, name, password, high_score):
        self.name = name
        self.values = {'password': password, 'high_score': high_score}

class HashTable:
    def __init__(self):
        self.table = [-1 for i in range(1000)]
    def insert(self, row_obj):
        'row object must have type(str) name attribute'
        name = row_obj.name
        hash_value = sum([ord(char)**2 for char in name[:5]])
        pos = hash_value % len(self.table)
        print(pos)

