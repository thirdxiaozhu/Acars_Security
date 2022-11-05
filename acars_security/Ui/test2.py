import socket
udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpServer.bind(("127.0.0.1", 5556))

while True:
    data, xxx = udpServer.recvfrom(8192)
    data = data.decode()
    
    print(data)