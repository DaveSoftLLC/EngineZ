import json
from http.server import BaseHTTPRequestHandler, HTTPServer
hostName = "127.0.0.1"
hostPort = 4443
lastMessage = {'user': 'startupNULL', 'message': 'startupNULL'}
class MyServer(BaseHTTPRequestHandler):
    #   GET is for clients geting the predi
    def do_GET(self):
        self.send_response(200)
        self.wfile.write(bytes("<p>You accessed path: %s</p>" % self.path, "utf-8"))

    #   POST is for submitting data.
    def do_POST(self):

	#print( "incomming http: ", self.path )

        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        
        post_data_cleaned = post_data.decode("utf-8").split("^`") 
        #print(post_data_cleaned)
        
        self.send_response(200, "OK")
        self.end_headers()
        #self.wfile.write(bytes("", "utf-8"))

        receivedJSON = post_data_cleaned[0]
        print(receivedJSON)
        receivedDict = json.loads(receivedJSON)
        print(receivedDict)
        
        if (receivedDict['command'] == "putChat"):
            self.wfile.write(bytes(addToChat(str(receivedDict['user']),str(receivedDict['message']), "utf-8"))
        elif (receivedDict['command'] == "getChat"):
            self.wfile.write(bytes(returnLatestMessage(), "utf-8"))
            
        #client.close()
            
def log_message(self, format):
    return

def addToChat(user,message):
    global lastMessage
    lastMessage['user'] = user
    lastMessage['message'] = message

def returnLatestMessage():
    global lastMessage
    dic = {}
    dic['command'] = 'processResponse'
    dic['user'] = lastMessage['user']
    dic['message'] = lastMessage['message']
    returnMessage = json.dumps(dic, ensure_ascii=False)
    print(returnMessage)
    return returnMessage
    
myServer = HTTPServer((hostName, hostPort), MyServer)
print("starting server")
try:
    myServer.serve_forever()
except KeyboardInterrupt:
    running = False
    pass

myServer.server_close()
