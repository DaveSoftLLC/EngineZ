import socket
TCP_IP = '192.227.178.111'
TCP_PORT = 5005
BUFFER_SIZE = 100 
while 1:
    MESSAGE = input('Enter text')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE.encode('utf-8'))
    data = s.recv(BUFFER_SIZE)
    s.close()
    print("received data:", data.decode('utf-8'))
    if MESSAGE == 'QUIT':
        break
    
#GAME
