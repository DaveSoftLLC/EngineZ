#James Xu
#MySQL library
#Works in conjunction with DigitalOcean server
from argon2 import PasswordHasher #password hashing lib (won some competition)
import MySQLdb as sql #lower level mysql lib


class MySQLRequest:
    def __init__(self, host, username, password, database):
        'Sends MySQL requests'
        self.host = host
        self.username = username
        self.password = password
        self.database = database

    def select(self, table, username):
        'Selects password hash from table'
        db = sql.connect(host=self.host,
                         user=self.username,
                         password=self.password,
                         db=self.database)
        #^^^ Connect to database
        cur = db.cursor()
        cur.execute("SELECT password_hash FROM " + table + " WHERE username='" + username + "'") #Execute query
        if cur.rowcount < 1: #Make sure there's a result
            return False
        else:
            for row in cur.fetchall():#Should only have one row as usernames are unique
                return row[0] #Only returns password_hash, so only one result
        db.close()
    def insert(self,table, username, password):
        'Inserts a new user into database'
        ph = PasswordHasher()
        db = sql.connect(host=self.host,
                         user=self.username,
                         password=self.password,
                         db=self.database)
        cur = db.cursor()
        hashed_password = ph.hash(password) #Hashed password
        cur.execute("INSERT INTO %s (username,password_hash,highscore) VALUES ('%s','%s',0)" #Execute insertion query
                    %(table,username,hashed_password))
        db.commit()#Commit changes
        db.close()
    def modify(self,username,score):
        'Adds new score to current score'
        db = sql.connect(host=self.host,
                         user=self.username,
                         password=self.password,
                         db=self.database)
        cur = db.cursor()
        cur.execute("SELECT highscore FROM users WHERE username='%s';" %username) #Make sure user exists
        if cur.rowcount != 1:
            raise ValueError('Username not Found/Unique') #Raise an error if more or less than one user exists
        old_score = cur.fetchall()[0][0]
        cur.execute("UPDATE users SET highscore = %d WHERE username = '%s';" %(old_score+score,username))#Update 
        db.commit()#Commit changes
        db.close()
