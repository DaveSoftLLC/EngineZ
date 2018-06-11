#!/usr/local/bin/python3
import cgitb
import cgi
import authenticate
from argon2 import PasswordHasher
cgitb.enable()
print("Content-Type: text/html")    # HTML is following
print()                             # blank line, end of headers
form = cgi.FieldStorage()
if "username" not in form or "password" not in form:
    print("<H1>Error</H1>")
    print("Please fill in the form properly!")
    return

ph = PasswordHasher()
username = form['username'].value
password = form['username'].value
hashed_password = ph.hash(password)
r = authenticate.MySQLRequest()
if not r.select('users',username):
    r.insert('users',username,hashed_password)
