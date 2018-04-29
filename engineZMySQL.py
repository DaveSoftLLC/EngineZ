import MySQLdb
from passlib.hash import pbkdf2_sha256
class mySQLrequest:
     def __init__(self):
          self.hosttxt = "s01.jamesxu.ca"
          self.usertxt = "mh4"
          self.passwdtxt = "a"
          self.dbname = "engineZ"
     def entryExists(self,user):
          db = MySQLdb.connect(host=self.hosttxt,    # your host, usually localhost
                          user=self.usertxt,         # your username
                          passwd=self.passwdtxt,  # your password
                          db=self.dbname)        # name of the data base

          # you must create a Cursor object. It will let
          #  you execute all the queries you need
          cur = db.cursor()

          # Use all the SQL you like
          cur.execute("SELECT * FROM leaderboard WHERE playerName='" + user + "'")
               
          # print all the first cell of all the rows
          if(cur.rowcount < 1):
               return False
          else:
               return True
          
     def mysqlUpdate(self,user,score=None,data=""):
          db = MySQLdb.connect(host=self.hosttxt,    # your host, usually localhost
                          user=self.usertxt,         # your username
                          passwd=self.passwdtxt,  # your password
                          db=self.dbname)        # name of the data base

          # you must create a Cursor object. It will let
          #  you execute all the queries you need
          cur = db.cursor()

          # Use all the SQL you like
          if(score == None):
               #update data
               sqlcommand = "UPDATE leaderboard SET additionalData='" + data + "' WHERE user='"+ user + "'"
          else:
               #update score
               sqlcommand = "UPDATE leaderboard SET score='" + str(score) + "' WHERE user='"+ user + "'"
          
          cur.execute(sqlcommand)

          # print all the first cell of all the rows
              
          db.commit()
          db.close()
          
     def mysqlInsert(self,user,data,score=None):
          db = MySQLdb.connect(host=self.hosttxt,    # your host, usually localhost
                          user=self.usertxt,         # your username
                          passwd=self.passwdtxt,  # your password
                          db=self.dbname)        # name of the data base

          # you must create a Cursor object. It will let
          #  you execute all the queries you need
          cur = db.cursor()

          # Use all the SQL you like
          sqlcommand = "INSERT INTO leaderboard (playerName,score,additionalData) VALUES ('" + user + "','" + str(score) + "','" + data + "')"
          
          cur.execute(sqlcommand)

          # print all the first cell of all the rows
              
          db.commit()
          db.close()

     def userAuthenticated(self,user,password):
          db = MySQLdb.connect(host=self.hosttxt,    # your host, usually localhost
                          user=self.usertxt,         # your username
                          passwd=self.passwdtxt,  # your password
                          db=self.dbname)        # name of the data base

          # you must create a Cursor object. It will let
          #  you execute all the queries you need
          cur = db.cursor()
          
          # Use all the SQL you like
          sqlcommand = "SELECT password FROM authentication WHERE playerName='" + user + "'"
          cur.execute(sqlcommand)
               
          # print all the first cell of all the rows
          if(cur.rowcount < 1):
               return False
          else:
               for row in cur.fetchall():
                      storedHash = row[0]
                      return pbkdf2_sha256.verify(givenHash, storedHash);
