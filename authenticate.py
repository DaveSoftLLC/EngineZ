from argon2 import PasswordHasher
import MySQLdb as sql


class MySQLRequest:
    def __init__(self, host, username, password, database):
        self.host = host
        self.username = username
        self.password = password
        self.database = database

    def select(self, table, username):
        db = sql.connect(host=self.host,
                         user=self.username,
                         password=self.password,
                         db=self.database)

        cur = db.cursor()
        cur.execute("SELECT password_hash FROM " + table + " WHERE username='" + username + "'")
        if cur.rowcount < 1:
            return False
        else:
            for row in cur.fetchall():
                return row[0]
        db.close()
    def insert(self,table, username, password):
        ph = PasswordHasher()
        db = sql.connect(host=self.host,
                         user=self.username,
                         password=self.password,
                         db=self.database)
        cur = db.cursor()
        hashed_password = ph.hash(password)
##        print("INSERT INTO %s (username,password_hash,highscore) VALUES ('%s','%s',0)"
##                    %(table,username,hashed_password))
        cur.execute("INSERT INTO %s (username,password_hash,highscore) VALUES ('%s','%s',0)"
                    %(table,username,hashed_password))
        db.commit()
        db.close()
    def modify(self,username,score):
        db = sql.connect(host=self.host,
                         user=self.username,
                         password=self.password,
                         db=self.database)
        cur = db.cursor()
        cur.execute("SELECT highscore FROM users WHERE username='%s';" %username)
        if cur.rowcount != 1:
            raise ValueError('Username not Found/Unique')
        old_score = cur.fetchall()[0][0]
        cur.execute("UPDATE users SET highscore = %d WHERE username = '%s';" %(old_score+score,username))
        db.commit()
        db.close()
        
        
if __name__ == '__main__':
    d = MySQLRequest('159.203.101.135', 'jamesxu', 'enginez123', 'enginez')
##    print(d.select('users','pay2lose'))
    d.modify('pay2lose',100)
