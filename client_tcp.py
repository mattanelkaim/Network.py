import socket

IP, PORT = "127.0.0.1", 8820
MESSAGE = "Hello There"

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect((IP, PORT))
my_socket.send(MESSAGE.encode())

data = my_socket.recv(1024).decode()
print(data)
my_socket.close()
