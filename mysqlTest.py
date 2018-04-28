import MySQLdb
hosttxt = "localhost"
usertxt = "mh4"
passwdtxt = "a"
dbname = "engineZ"
def entryExists(user):
     global hosttxt,usertxt,passwdtxt,dbname
     db = MySQLdb.connect(host=hosttxt,    # your host, usually localhost
                     user=usertxt,         # your username
                     passwd=passwdtxt,  # your password
                     db=dbname)        # name of the data base

          # you must create a Cursor object. It will let
          #  you execute all the queries you need
     cur = db.cursor()

          # Use all the SQL you like
     cur.execute("SELECT * FROM leaderboard WHERE playerName='" + user + "'")
          
          # print all the first cell of all the rows
     for row in cur.fetchall():
          if(len(row[1]) < 1):
               db.close()
               return False
          else:
               db.close()
               return True
          
def mysqlUpdate(user,score=None,data=""):
     global hosttxt,usertxt,passwdtxt,dbname
     db = MySQLdb.connect(host=hosttxt,    # your host, usually localhost
                     user=usertxt,         # your username
                     passwd=passwdtxt,  # your password
                     db=dbname)        # name of the data base

     # you must create a Cursor object. It will let
     #  you execute all the queries you need
     cur = db.cursor()

     # Use all the SQL you like
     if(score == None):
          #update data
          sqlcommand = "UPDATE leaderboard SET additionalData='" + data + "' WHERE user='"+ user "'"
     else:
          #update score
          sqlcommand = "UPDATE leaderboard SET score='" + str(score) + "' WHERE user='"+ user "'"
     
     cur.execute(sqlcommand)

     # print all the first cell of all the rows
         
     db.commit()
     db.close()
     
def mysqlInsert(user,score=None,data):
     global hosttxt,usertxt,passwdtxt,dbname
     db = MySQLdb.connect(host=hosttxt,    # your host, usually localhost
                     user=usertxt,         # your username
                     passwd=passwdtxt,  # your password
                     db=dbname)        # name of the data base

     # you must create a Cursor object. It will let
     #  you execute all the queries you need
     cur = db.cursor()

     # Use all the SQL you like
     sqlcommand = "INSERT INTO leaderboard (playerName,score,additionalData) VALUES ('" user + "','" + str(score) + "','" + data"')"
     
     cur.execute(sqlcommand)

     # print all the first cell of all the rows
         
     db.commit()
     db.close()
     
print(entryExists("lol"));
