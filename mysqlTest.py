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
     cur.execute("SELECT * FROM leaderboard WHERE playerName=" + user)
          
          # print all the first cell of all the rows
     for row in cur.fetchall():
          if(len(row[1]) < 1):
               db.close()
               return False
          else:
               db.close()
               return True
          
def mysqlStuff(insert,user="",score="",data=""):
     if(insert):
          
          db = MySQLdb.connect(host=hosttxt,    # your host, usually localhost
                     user=usertxt,         # your username
                     passwd=passwdtxt,  # your password
                     db=dbname)        # name of the data base

          # you must create a Cursor object. It will let
          #  you execute all the queries you need
          cur = db.cursor()

          # Use all the SQL you like
          cur.execute("SELECT * from  leaderboard")

          # print all the first cell of all the rows
          for row in cur.fetchall():
              print(row[0])

          db.close()
     else:
          db = MySQLdb.connect(host=hosttxt,    # your host, usually localhost
                     user=usertxt,         # your username
                     passwd=passwdtxt,  # your password
                     db=dbname)        # name of the data base

          # you must create a Cursor object. It will let
          #  you execute all the queries you need
          cur = db.cursor()

          # Use all the SQL you like
          cur.execute("SELECT * FROM leaderboard")

          # print all the first cell of all the rows
          for row in cur.fetchall():
              print(row[0])

          db.close()
mysqlStuff("hi");
print(entryExists("lol"));
