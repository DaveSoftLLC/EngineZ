import MySQLdb
def mysqlStuff(data):
     db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="engineZ",         # your username
                     passwd="engineZ",  # your password
                     db="engineZ")        # name of the data base

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
