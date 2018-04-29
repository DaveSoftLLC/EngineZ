import pickle, socket

lis = [['bleed',150000]]
nLis = ['season = grey[‘anatomy’][2].finale']
var = bytes('','utf-8')
var2 = bytes('','utf-8')
for i in lis:
    for a in range(1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('192.168.4.1',1511))
        s.sendall(pickle.dumps(i))
        for i in range(50):
            data = s.recv(10000)
            var += data
        s.close()

print(pickle.loads(var))
