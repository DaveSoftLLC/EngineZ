import socket
TCP_IP = '192.227.178.111'
TCP_PORT = 5005
BUFFER_SIZE = 100  # Normally 1024, but we want fast response
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
print 'Beginning Server'
s.listen(1)
while 1:
	conn, addr = s.accept()
	conn.send('Connection Approved'.encode('utf-8'))
	print('Connection address:', addr)
	data = conn.recv(BUFFER_SIZE)
	if not data: continue
	decoded = data.decode('utf-8')
	if decoded == 'QUIT':
		conn.send("Received: QUIT".encode('utf-8'))
		break
	else:
		print decoded
		conn.send('Received Data'.encode('utf-8'))
conn.close()
	
